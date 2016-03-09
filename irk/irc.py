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
import rlcompleter
import getpass
import logging

from utils import cwdopen, pretty, timestamp

default_config = {
    'host': 'irc.foonetic.net', 'port': 7001, 'ipv6': False,
    'nick': '', 'pass': '',
    'ident': '', 'user': '',
    'mode': '+B', 'unused': '*',
    'owner': '',
    'channels': [],
    'logging': True, 'log_level': 'DEBUG'
 }

# TODO: Make the parts more modular, no need for hacked together parts..
# TODO:


# TODO: Move and compile all regexes. Better logging, more commenting, etc
# TODO: Code is really monolithic, many things could be broken down...
# eventually __init__() should only have methods in it...for good modularity
class IrcClient:
    def __init__(self, directory, interactive=True):
        # Find (make) irc client home directory as well as its subfolders.
        self.init_homedir(directory)

        # Create, open and check the configuration file. TODO: More robust, break down
        # It assumes existing files are valid... Lots of bad things
        self.init_config()
        
        # So far logging will only support one file per class, needs to be
        # one file per server. Plus, for regular IRC activity, logging should be
        # plain. I don't think I should use logging library for that.
        self.init_logging()

        # TODO: Load plugins (live reload)

    def init_homedir(self, directory):
        if not os.path.isabs(directory):
            root = os.path.expanduser("~")
        else:
            root = ''

        self.homedir = os.path.join(root, directory)
        self.folders = ["plugins", "logs"]

        if not os.path.exists(self.homedir):
            os.makedirs(self.homedir)

        for i, folder in enumerate(self.folders):
            self.folders[i] = os.path.join(self.homedir, folder)
            if not os.path.exists(self.folders[i]):
                os.mkdir(self.folders[i])        
    
    def init_config(self):
        config_file = os.path.join(self.homedir, "config")
        if not os.path.exists(config_file):
            with cwdopen(config_file, 'w') as file:
                json.dump(default_config, file, indent=2)

        with cwdopen(config_file, 'r') as file:
            self.config = json.load(file)

        changed = False

        # I could wrap the input in a try/except case and check for valueerrors to force
        # correct values #TODO move whole configuration code out of class
        # Check for interactivity
        for key, value in self.config.iteritems():
            if value is None or value == '' and key != 'pass':
                changed = True
                self.config[key] = str(raw_input(pretty("{}: ".format(key), 'CLI')))
            if key == 'pass' and value == '':
                self.config[key] = getpass.getpass(pretty("pass: ", 'CLI'))
            if key == 'channels' and value == []:
                changed = True
                print pretty("To finish, enter DONE.", 'CLI')
                while i != "DONE":
                    i = str(raw_input(pretty("channel: ", 'CLI')))
                    if i[0] == '#':
                        self.config[key].append(i)

        if changed:
            with cwdopen(config_file, 'w') as file:
                json.dump(self.config, file, indent=2)
                
    def init_logging(self):
        self.logger = None
        if bool(self.config['logging']):
            log_level = None
            server_name = self.config['host'].split('.')[1]
            log_file = os.path.join(self.homedir, self.folders[1],
                                    "{0}.log".format(server_name))

            if 'log_level' not in self.config:
                log_level = logging.INFO
            else:
                ll = self.config['log_level']
                if ll == "DEBUG":
                    log_level = logging.DEBUG
                elif ll == "INFO":
                    log_level = logging.INFO
                elif ll == "WARNING":
                    log_level = logging.WARNING
                elif ll == "ERROR":
                    log_level = logging.ERROR
                elif ll == "CRITICAL":
                    log_level = logging.CRITICAL

            logging.basicConfig(level=log_level)
            self.logger = logging.getLogger("irc")
            self.logger.addHandler(logging.FileHandler(log_file, 'a+'))

    def start(self):
        self.init_socket()
        self.sock.connect((self.config['host'], int(self.config['port'])))

        ssl_info = self.sock.cipher()
        if ssl_info:
            m = pretty("SSL Cipher ({0}), SSL Version ({1}), SSL Bits ({2})".format(*ssl_info), 'INFO')
            if self.logger:
                self.logger.info(m)
            else:
                print m
        # IRC RFC2812:3.1 states that a client needs to send a nick and
        # user message in order to register a connection.
        self.nick()
        self.user()

        self.txrx_loop()

    def stop(self):
        self.quit()
        self.sock.close()

    def init_socket(self):
        self.sock = None
        """Initialize the socket connection."""
        if self.config['ipv6']:
            sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0)
        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.sock = ssl.wrap_socket(sock)

    def txrx_loop(self):
        """Transmit/Receive loop"""
        while True:
            # Get a raw 4kb chunk of data from the socket.
            data = self.sock.recv(4096)
            if not data:
                m = pretty("No more data... Connection closed.", 'ERROR')
                if self.logger:
                    self.logger.error(m)
                else:
                    print m
                break

            # IRC RFC2812:2.3 states IRC messages always end with '\r\n'
            # Split the data into the IRC message sit contains.
            messages = data.split('\r\n')
            for message in messages:
                if message:
                    self.process_msg(message)

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
        else:
            command, params = message.split(' ', 1)

        # TODO: check interactive? Work on interactive/nohead modes
        m = pretty(message, 'RECEIVE')

        if self.logger:
            self.logger.info(m)
        else:
            print m

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
                self.config['nick'] = "_{}".format(self.config['nick'])
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
        m = pretty(message, 'SEND')
        if self.logger:
            self.logger.info(m)
        else:
            print m

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
