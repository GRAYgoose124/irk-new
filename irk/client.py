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

from PyQt5 import QtCore

from irk.protocol import IrcProtocol

logger = logging.getLogger(__name__)

# See docs/IrcClientAPI for configuration format information.
basic_irc_config = {
    'host': '', 'port': 7001, 'ipv6': False,
    'nick': '', 'pass': '',
    'ident': '', 'user': '',
    'mode': '+B', 'unused': '*',
    'owner': '', 'owner_email': '',
    'channels': []
}


def init_irc_config(config_file):
    if not os.path.exists(config_file):
        with open(config_file, 'w') as f:
            json.dump(basic_irc_config, f, indent=2)

    changed = False
    config = json.load(open(config_file, 'r'))

    for key, value in config.items():
        if value is None or value == '' and key != 'pass':
            config[key] = str(input(''.join((key, '> '))))
            changed = True

        elif key == 'pass' and value == '':
            config[key] = getpass.getpass("pass: ")
            changed = True

        elif key == 'channels' and value == []:
            string = None
            print("To finish, enter DONE.")

            while string != 'DONE':
                string = str(input("channel: "))
                if string[0] == '#':
                    config[key].append(string)
            changed = True

    if changed:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)

    for key, value in basic_irc_config.items():
        if key not in config:
            config = None

    return config


class IrcClient(QtCore.QObject):
    # TODO: Merge these signals?
    message_sent = QtCore.pyqtSignal(str)
    message_received = QtCore.pyqtSignal(str)

    channel_joined = QtCore.pyqtSignal(str)
    channel_part = QtCore.pyqtSignal(str)

    privmsg_event = QtCore.pyqtSignal(dict)

    def __init__(self, config):
        super(IrcClient, self).__init__()

        self.sock = None
        self.config = config

        if self.config is None:
            raise ValueError("Configuration file error.")

        self.irc_commands = {}
        self.joined_channels = []

    def start(self):
        logger.info("Client started.")
        if self.sock is None:
            self._init_socket()

            ssl_info = self.sock.cipher()
            if ssl_info:
                logger.info("SSL Cipher (%s), SSL Version (%s), SSL Bits (%s)", *ssl_info)

            # IRC RFC2812:3.1 states that a client needs to send a nick and
            # user message in order to register a connection.
            # Most servers mandate that the user's real name be the owner.
            self.send_message(IrcProtocol.nick(self.config['nick']))
            self.send_message(IrcProtocol.user(self.config['user'], self.config['unused'], self.config['owner']))

            self.__loop()

    def stop(self):
        if self.sock is not None:
            self.send_message(IrcProtocol.quit())
            self.sock.close()
            self.sock = None

    def _init_socket(self):
        if self.config['ipv6']:
            sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0)
        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if sock is not None:
            self.sock = ssl.wrap_socket(sock)
            self.sock.connect((self.config['host'], int(self.config['port'])))
        else:
            self._init_socket()


        logger.debug(self.sock)


    def __loop(self):
        """Transmit/Receive loop"""
        while self.sock is not None:
            try:
                # TODO: Major glitch...can't stop/restart correctly.
                data = self.sock.recv(2048)
            except:
                logger.error(data)
                logger.info("No more data... Connection closed.")
                self.sock.close()
                self.sock = None

            # IRC RFC2812:2.3
            messages = data.split(b'\r\n')
            for message in messages:
                if message:
                    self.__process_message(message)



    def send_response(self, message, original_sender=None, destination=None):
        if destination is not None and destination[0] == '#':
            self.send_message(IrcProtocol.privmsg(destination, message))
        elif original_sender is not None:
            self.send_message(IrcProtocol.privmsg(original_sender, message))

    def send_message(self, message, limit=512):
        """ Send a basic IRC message over the socket."""
        if len(message) >= (limit - 2):
            message = message[:limit - 2]

        if self.sock is not None:
            self.sock.send(bytes("{0}\r\n".format(message), 'ascii'))
            message = re.sub("NICKSERV :(.*) .*", "NICKSERV :\g<1> <password>", message)

            self.message_sent.emit(message)
        else:
            logger.debug("Tried to send message without a socket! message(%s)", message)
            message = None

        return message

    # Move commands to dict/funcs/parser class?
    def __process_message(self, message):
        """Process IRC messages."""
        message = message.decode('ascii')
        self.message_received.emit(message)

        prefix, command, parameters = IrcProtocol.split_message(message)
        sender, user, ident = IrcProtocol.parse_prefix(prefix)

        if command == 'PRIVMSG':
            if prefix is None:
                logger.debug("Malformed PRIVMSG: %s", message)
                return

            tokens = parameters.split(' ')
            original_destination = tokens[0]
            privmsg_command = tokens[1][1:]
            arguments = tokens[2:]
            data_packet = {'sender': sender,
                           'ident': ident,
                           'original_destination': original_destination,
                           'message': privmsg_command + " " + " ".join(tokens[2:])}

            # CTCP PRIVMSGs
            if privmsg_command == '\x01PING':
                time_stamp_copy = " ".join((arguments[0], arguments[1][:-1]))
                self.send_message(IrcProtocol.notice(data_packet['sender'],
                                                     IrcProtocol.wrap_ctcp(" ".join(("PING", format(time_stamp_copy))))))
            elif privmsg_command[0] == '\x01':
                logger.debug('Missing CTCP command %s', privmsg_command)

            self.privmsg_event.emit(data_packet)

        elif command == 'NOTICE':
            pass

        elif command == 'JOIN':
            self.joined_channels.append(parameters[1:])
            self.channel_joined.emit(parameters[1:])
            logger.info("Joined channel: %s", self.joined_channels)

        elif command == 'PART':
            if sender == self.config['nick']:
                self.channel_part.emit(parameters.split(" ")[0])

        # Auto-join servers after MODE received from NickServ.
        elif command == 'MODE':
            if prefix.lower() == ':nickserv':
                for channel in self.config['channels']:
                    self.send_message(IrcProtocol.join(channel))

        # PONG any server PINGs with the same parameters.
        elif command == 'PING':
            self.send_message(IrcProtocol.server_pong(parameters))

        # Set the bot's mode on server join after 001 received.
        elif command == '001':
            self.send_message(IrcProtocol.mode(self.config['nick'], self.config['mode']))

        # Identify yourself when connection is ready.
        elif command == '376':
            if self.config['nick'] != '' and self.config['nick'][0] != '_':
                self.send_message(IrcProtocol.identify(self.config['pass']))

        elif command == '433':
            if re.search("Nickname is already in use", parameters):
                self.config['nick'] = "_{}".format(self.config['nick'])
                self.send_message(IrcProtocol.nick(self.config['nick']))
                self.send_message(IrcProtocol.user(self.config['user'], self.config['unused'], self.config['owner']))
                self.send_message(IrcProtocol.mode(self.config['nick'], self.config['mode']))

        else:
            logger.debug("Missing IRC command: %s (%s)", command, parameters)
