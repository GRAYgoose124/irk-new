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
import readline
import rlcompleter
import getpass
import logging
import sys

from utils import cwdopen, pretty
from ircprotocol import IrcProtocol
import irctools

logger = logging.getLogger(__name__)


# TODO Sort into channels/queries in client or bot? buffer? log it.
class IrcClient(IrcProtocol):
    def __init__(self, directory, config, interactive=True):
        self.homedir = directory
        self.config = config

        # Validate configuration.
        isvalid = True
        for key, value in irctools.required_irc_config.iteritems():
            if key not in self.config:
                isvalid = False
                logger.error("Missing key: %s", key)
        if not isvalid:
            raise ValueError("Required keys missing from configuration.")
        # TODO: channels/queries 

    def start(self):
        self.init_socket()

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

    # Thread receive loop
    def _loop(self):
        """Transmit/Receive loop"""
        while True:
            # Get a raw 4kb chunk of data from the socket.
            data = self.sock.recv(4096)
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

    def _proc_msg(self, message):
        """Process IRC messages."""
        # Split the message into it's prefix, command, and parameters.
        prefix, command, params = None, None, None
        # function-ize this part
        if message[0] == ':':
            prefix, msg = message.split(' ', 1)
            if ' ' in msg:
                command, params = msg.split(' ', 1)
            else:
                command = msg
        else:
            command, params = message.split(' ', 1)
        # Parse Prefix
        if prefix is not None:
            if '!' in prefix:
                sender_nick = prefix.split('!')[0][1:]
                hostname = prefix.split('!')[1]
                if '@' in hostname:
                    hostname = hostname.split('@')[1]
            else:
                sender_nick = prefix
                hostname = prefix
            
        # TODO: Put in dict/hash O(n) search
        # PRIVMSG and NOTICE is where the magic happens.
        # TODO: Organize into logical channels/queries and output to bot.
        if command == 'PRIVMSG':
            if prefix is None:
                logger.debug("Malformed PRIVMSG: %s", message)
                return
            tokens = params.split(' ')
            bot_cmd = tokens[1][1:]

            # Reply to CTCP PINGS TODO: modify to catch all CTCP
            if bot_cmd == '\x01PING':
                self.notice_ping(sender_nick, "\x01{0} {1}\x01".format(tokens[2],
                                                                tokens[3][:-1]))
            elif bot_cmd[0] == '\x01':
                logger.debug('Missing CTCP command %s', cmd[1:])
            else:
                print bot_cmd
                self.proc_privmsg((sender_nick, hostname), bot_cmd, tokens[2:])
        elif command == 'NOTICE':
            self.proc_notice((sender_nick, hostname), prefix, params)
        elif command == 'MODE':
            if prefix.lower() == ':nickserv':
                # Join channels in config automatically 
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
            logger.debug("Missing command: {}".format(command))

    def proc_notice(self, prefix, params):
        raise NotImplementedError("{0}.{1}".format(self.__class__.__name__, "_proc_notice()")) 

    def proc_privmsg(self, sender_nick, command, params):
        raise NotImplementedError("{0}.{1}".format(self.__class__.__name__, "_proc_privmsg()"))



