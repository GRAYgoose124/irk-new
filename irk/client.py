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
import re
import logging
import socket
import ssl
import os
import json
import getpass

from utils import pretty, cwdopen
from protocol import IrcProtocol


logger = logging.getLogger(__name__)


required_irc_config = {
    'host': 'irc.foonetic.net', 'port': 7001, 'ipv6': False,
    'nick': '', 'pass': '',
    'ident': '', 'user': '',
    'mode': '+B', 'unused': '*',
    'owner': '', 'owner_email': '',
    'channels': []
 }


# TODO Sort into channels/queries in client or bot? buffer? log it.
class IrcClient(IrcProtocol):
    def __init__(self, directory):
        IrcProtocol.__init__(self)

        config_filename = os.path.join(directory, "config")
        self.config = self._init_config(config_filename)

        if self.config is None:
            raise ValueError("Configuration file error.")

    def start(self):
        self._init_socket()

        ssl_info = self.sock.cipher()
        if ssl_info:
            m = pretty("SSL Cipher ({0}), SSL Version ({1}), SSL Bits ({2})".format(*ssl_info),
                       'INFO')
            logger.debug(m)
            
        # IRC RFC2812:3.1 states that a client needs to send a nick and
        # user message in order to register a connection.
        self.nick()
        self.user()

        self._loop()

    def stop(self):
        self.quit()
        self.sock.close()

    def _init_socket(self):
        if self.config['ipv6']:
            sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0)
        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.sock = ssl.wrap_socket(sock)
        self.sock.connect((self.config['host'], int(self.config['port'])))

    # TODO: Thread receive loop? Thread plugins? Thread send?
    def _loop(self):
        """Transmit/Receive loop"""
        while True:
            data = self.sock.recv(2048)

            if not data:
                logger.info("No more data... Connection closed.")
                break

            # IRC RFC2812:2.3 states IRC messages always end with '\r\n'
            # Split the data into the IRC message sit contains.
            messages = data.split('\r\n')
            for message in messages:
                if message:
                    logger.info(pretty(message, 'RECEIVE'))
                    self._proc_msg(message)

        self.sock.close()

     # TODO: Put commands in table/dict/hash O(n) search structure.
    def _proc_msg(self, message):
        """Process IRC messages."""
        # Prefix check and simple parse
        prefix, command, params = None, None, None

        if message[0] == ':':
            prefix, msg = message.split(' ', 1)

            if ' ' in msg:
                command, params = msg.split(' ', 1)
            else:
                command = msg
        else:
            command, params = message.split(' ', 1)

        # Parse Prefix
        sender, ident = None, None

        if prefix is not None:
            if '!' in prefix:
                sender = prefix.split('!')[0][1:]
                ident = prefix.split('!')[1]

                if '@' in ident:
                    ident = ident.split('@')[1]
            else:
                sender = prefix
                ident = prefix

        # PRIVMSG is where the magic happens.
        if command == 'PRIVMSG':
            if prefix is None:
                logger.debug("Malformed PRIVMSG: %s", message)
                return

            tokens = params.split(' ')
            data = { 'sender': sender,
                     'ident': ident,
                     'orig_dest': tokens[0],
                     'command': tokens[1][1:],
                     'arguments': tokens[2:]
                     }

            # CTCP PRIVMSG
            if data['command'] == '\x01PING':
                time_stamp_copy = tokens[3][:-1]
                self.notice_ping(data['sender'], "{0} {1}".format(data['orig_dest'], time_stamp_copy))

            elif data['command'][0] == '\x01':
                logger.debug('Missing CTCP command %s', data['command'])

            # Run all plugins which provide a command_hook()
            self.process_privmsg_hooks(data)

        elif command == 'NOTICE':
            pass

        # Auto-join servers after MODE received from NickServ.
        elif command == 'MODE':
            if prefix.lower() == ':nickserv':
                for channel in self.config['channels']:
                    self.join(channel)

        # PONG any server PINGs with the same parameters.
        elif command == 'PING':
            self._msg("PONG {0}".format(params))

        # Set the bot's mode on server join after 001 received.
        elif command == '001':
            self.mode()

        # Identify yourself when connection is ready.
        elif command == '376':
            if self.config['nick'] != '':
                self.identify()

        elif command == '433':
            if re.match(":Nickname is already in use", params) is not None:
                self.config['nick'] = "_{}".format(self.config['nick'])
                self.mode()

        else:
            logger.debug(pretty("Missing IRC command: {0} ({1})".format(command, params), 'REC'))

    # TODO: Clean this up, make sure it's valid
    def _init_config(self, config_file):
        if not os.path.exists(config_file):
            with cwdopen(config_file, 'w') as file:
                json.dump(required_irc_config, file, indent=2)

        changed = False
        config = json.load(cwdopen(config_file, 'r'))

        for key, value in config.iteritems():
            if value is None or value == '' and key != 'pass':
                config[key] = str(raw_input(pretty("{}: ".format(key), 'CLI')))
                changed = True

            elif key == 'pass' and value == '':
                config[key] = getpass.getpass(pretty("pass: ", 'CLI'))
                changed = True

            elif key == 'channels' and value == []:
                i = None
                print pretty("To finish, enter DONE.", 'CLI')

                while i != "DONE":
                    i = str(raw_input(pretty("channel: ", 'CLI')))

                    if i[0] == '#':
                        config[key].append(i)

                changed = True

        if changed:
            with cwdopen(config_file, 'w') as file:
                json.dump(config, file, indent=2)

        for key, value in required_irc_config.iteritems():
            if key not in config:
                return None

        return config

    # Available Plugin Hooks
    def process_privmsg_hooks(self, data):
        raise NotImplementedError("{0}.{1}".format(self.__class__.__name__, "process_privmsg_hooks()"))



