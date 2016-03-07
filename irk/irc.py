#   Irk: irc bot
#   Copyright (C) 2016  Grayson Miller
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>
import socket
import ssl
import re
import json
import os
import readline
import getpass

from utils import cwdopen, log, timestamp


# log file should be given from the caller on init
default_config = {
    'host': 'irc.foonetic.net',
    'port': 7001,
    'nick': '',
    'pass': '',
    'ident': '',
    'user': '',
    "mode": '+B',
    "unused": '*',
    "owner": '',
    "logging": True,
    "channels": []
 }

# TODO: Fix logger, it's not good practice to wrap print, this one is inconsistent
# and far too intertwined.

# TODO: Make the parts more modular, no need for hacked together parts..
# TODO: 


# TODO: Move and compile all regexes. Better logging, more commenting, so much...
# TODO: Code is really monolithic, many things could be broken down...
# eventually __init__() should only have methods in it...for good modularity
class IrcClient:
    def __init__(self, homedir, interactive=True):
        self.sock = None

        # Find (make) irc client home directory as well as its subfolders
        # Offload this to a tree_init function
        if not os.path.isabs(homedir):
            root = os.path.expanduser("~")
        else:
            root = ''

        self.homedir = os.path.join(root, homedir)
        self.folders = ["plugins", "logs"]

        if not os.path.exists(self.homedir):
            os.makedirs(self.homedir)

        for i, folder in enumerate(self.folders):
            self.folders[i] = os.path.join(self.homedir, folder)
            if not os.path.exists(self.folders[i]):
                os.mkdir(self.folders[i])

        # Create, open and check the configuration file. TODO: More robust, break down
        # It assumes existing files are valid... Lots of bad things.
        config_file = os.path.join(self.homedir, "config")
        if not os.path.exists(config_file):
            with cwdopen(config_file, 'w') as file:
                json.dump(default_config, file, indent=2)

        with cwdopen(config_file, 'r') as file:
            self.config = json.load(file)

        changed = False

        # I could wrap the input in a try/except case and check for valueerrors to force
        # correct values #TODO move whole configuration code out of class
        for key, value in self.config.iteritems():
            if value is None or value == '' and key != 'pass':
                changed = True
                self.config[key] = str(raw_input("CLI| {}: ".format(key)))
            if key == 'pass' and value == '':
                self.config[key] = getpass.getpass("CLI| pass: ")
            if key == 'channels' and value == []:
                changed = True
                print "CLI| To finish, enter DONE."
                while i != "DONE":
                    i = str(raw_input("CLI| channel: "))
                    if i[0] == '#':
                        self.config[key].append(i)

        if changed:
            with cwdopen(config_file, 'w') as file:
                json.dump(self.config, file, indent=2)

        # Handle logging. TODO: Offload to Logging, separate from calss
        if bool(self.config['logging']):
            log_file = os.path.join(self.homedir, self.folders[1],
                                    "{0}.log".format(self.config['host']))
            self.log_file = cwdopen(log_file, 'a+')
        else:
            self.log_file = None

        # TODO: Load plugins (live reload)

    def init_config(self, data, file):
        pass

    def start(self):
        self.init_socket()
        self.sock.connect((self.config['host'], int(self.config['port'])))

        ssl_info = self.sock.cipher()
        if ssl_info:
            log("SSL Cipher ({0}), SSL Version ({1}), SSL Bits ({2})".format(*ssl_info), self.log_file, 'INFO')

        # IRC RFC2812:3.1 states that a client needs to send a nick and
        # user message in order to register a connection.
        self.nick()
        self.user()

        self.txrx_loop()

    def stop(self):
        self.quit()
        self.sock.close()
        self.log_file.close()

    def init_socket(self):
        """Initialize the socket connection."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock = ssl.wrap_socket(sock)

    def txrx_loop(self):
        """Transmit/Receive loop"""
        while True:
            # Get a raw 4kb chunk of data from the socket.
            data = self.sock.recv(4096)
            if not data:
                log("No more data... Connection closed.", self.log_file, 'ERROR')
                break

            # IRC RFC2812:2.3 states IRC messages always end with '\r\n'
            # Split the data into the IRC message sit contains.
            messages = data.split('\r\n')
            for message in messages:
                if message:
                    self.process_msg(message)

            self.log_file.flush()
        self.sock.close()

    def process_msg(self, message):
        """Process IRC messages."""
        prefix, command, params = None, None, None

        if message[0] == ':':
            prefix, msg = message.split(' ', 1)
            if ' ' in msg:
                command, params = msg.split(' ', 1)
            else:
                command = msg
                params = None
        else:
            command, params = message.split(' ', 1)

        log("{0}".format(message), self.log_file, 'RECEIVE')

        # TODO: Sort for performance?
        # clean up command parsing
        if command == 'PING':
            self.msg("PONG {0}".format(params))
        elif command == 'MODE':
            if prefix.lower() == ':nickserv':
                for channel in self.config['channels']:
                    self.join(channel)
        elif command == 'PRIVMSG':
            self.process_privmsg(prefix, params)
        elif command == 'NOTICE':
            pass
        elif command == '001':
            self.mode()
        elif command == '376':
            if self.nick:
                self.identify()
        elif command == '433':
            if re.match(":Nickname is already in use", params) is not None:
                self.config['nick'] = '_' + self.config['nick']
                self.mode()

    # TODO: Offload to Bot class. Add more commands.
    # TODO: clean up command parsing
    def process_privmsg(self, prefix, params):
        sender_nick = prefix.split('!')[0][1:]
        tokens = params.split(' ')
        command = tokens[1][1:]

        # Reply to CTCP PINGS
        if command == '\x01PING':
            self.notice_ping(sender_nick, "{0} {1}".format(tokens[2],
                                                           tokens[3][:-1]))

        # Protected cmds TODO: Add privileges
        elif sender_nick == self.config['owner']:
            if command == '!quit':
                self.quit()
            elif command == '!ping':
                if len(tokens) > 2:
                    self.privmsg_ping(tokens[2])
                else:
                    self.privmsg_ping(sender_nick)

    # IRC Messages
    def msg(self, message):
        self.sock.send("{0}\r\n".format(message))
        message = re.sub("NICKSERV :(.*) .*", "NICKSERV :\g<1> <password>",
                         message)
        log("{0}".format(message), self.log_file, 'SEND')

    # Refactor notice and privmsg out or fix how ctcp calls them...
    def notice(self, destination, message):
        self.msg("NOTICE {0} :{1}".format(destination, message))

    def privmsg(self, destination, message):
        self.msg("PRIVMSG {0} :{1}".format(destination, message))

    def nick(self):
        self.msg("NICK {0}".format(self.config['nick']))

    def user(self):
        self.msg("USER {0} {1} {2} {3}".format(self.config['user'], 0,
                                               self.config['unused'],
                                               self.config['owner']))

    def mode(self):
        self.msg("MODE {0} {1}".format(self.config['nick'],
                                       self.config['mode']))
    def join(self, channel):
        self.msg("JOIN {0}".format(channel))

    def quit(self, quit_msg='Quitting'):
        self.msg("QUIT :{0}".format(quit_msg))

    def register(self):
        self.privmsg("NICKSERV",
                     "REGISTER {0} {1}".format(self.config['owner_email'],
                                               self.config['pass']))
    def identify(self):
        self.privmsg("NICKSERV",
                     "IDENTIFY {0}".format(self.config['pass']))

    # TODO: SRSLY FIX THIS SHIT / PING TOO
    def ctcp(self, msg_func, destination, message):
        msg_func(destination, "\x01{0}\x01".format(message))

    def privmsg_ping(self, destination):
        #Time the time it takes to receive pong
        time = str(timestamp())
        self.ctcp(self.privmsg, destination,
                  "PING {0} {1}".format(time[:10], time[10:]))

    def notice_ping(self, destination, params):
        self.ctcp(self.notice, destination, "PING {0}".format(params))
