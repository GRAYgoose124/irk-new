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

from utils import cwdopen, log, timestamp

default_config = """{
  "host": "irc.foonetic.net",
  "port": "6697",
  "nick": "bot",
  "pass": "None",
  "ident": "None",
  "user": "None",
  "mode": "+B",
  "unused": "None",
  "owner": "None",
  "logging": "True",
  "log_file": "foonetic"
}"""

# TODO: Move and compile all regexes.
class IrcClient:
    def __init__(self, path=".irk", putinhome=True):
        if putinhome == True:
            home = os.path.expanduser("~")
        else:
            home = ''

        self.path = os.path.join(home, path)
        if not os.path.exists(self.path):
            os.mkdir(self.path)

        # TODO: plugins, live reload
        if not os.path.exists(os.path.join(self.path, "config")):
            self.config = self.gen_config()
            with cwdopen(os.path.join(self.path, "config"), 'w+') as file:
                file.write(self.config)

        with cwdopen(os.path.join(self.path, "config"), 'r') as file:
            self.config = json.load(file)

        if bool(self.config['logging']):
            self.log_file = cwdopen(os.path.join(self.path, "{0}.log".format(self.config['log_file'])), 'a+')

        self.sock = None

    def gen_config(self, prompt=False):
        return default_config

    def start(self):
        self.init_socket()
        self.sock.connect((self.config['host'], int(self.config['port'])))

        ssl_info = self.sock.cipher()
        if ssl_info:
            log("SSL Cipher ({0}), SSL Version ({1}), SSL Bits ({2})".format(*ssl_info), self.log_file, 'INFO')

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
            data = self.sock.recv(8168)
            if not data:
                log("No more data... Connection closed.", self.log_file, 'ERROR')
                break

            messages = data.split('\r\n')
            for message in messages:
                if message:
                    self.process_msg(message)

            self.log_file.flush()
        self.sock.close()

    def process_msg(self, message):
        """Process IRC messages."""
        prefix, command, params = None, None, None

        try:
            if message[0] == ':':
                prefix, msg = message.split(' ', 1)
                if ' ' in msg:
                    command, params = msg.split(' ', 1)
                else:
                    command = msg
                    params = None
            else:
                command, params = message.split(' ', 1)
        except ValueError as e:
            log("{0}: {1}".format(repr(e), message), self.log_file, 'ERROR')

        log("{0}".format(message), self.log_file, 'RECEIVE')

        # TODO: Sort for performance?
        # clean up command parsing
        if command == 'PING':
            self.msg("PONG {0}".format(params))
        elif command == 'MODE':
            if prefix.lower() == ':nickserv':
                self.join("#freesoftware")
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
            self.notice_ping(sender_nick, "{0} {1}".format(tokens[2], tokens[3][:-1]))

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
        message = re.sub("NICKSERV :IDENTIFY .*",
                         "NICKSERV :IDENTIFY <password>", message)
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

    def identify(self):
        self.privmsg("NICKSERV",
                            "IDENTIFY {0}".format(self.config['pass']))

    # TODO: SRSLY FIX THIS SHIT / PING TOO
    def ctcp(self, msg_func, destination, message):
        msg_func(destination, "\x01{0}\x01".format(message))

    def privmsg_ping(self, destination):
        #Time the time it takes to receive pong
        time = str(timestamp())
        self.ctcp(self.privmsg, destination, "PING {0} {1}".format(time[:10], time[10:]))

    def notice_ping(self, destination, params):
        self.ctcp(self.notice, destination, "PING {0}".format(params))
