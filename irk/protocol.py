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
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>
import re
import logging
import string

from PyQt5 import QtCore

logger = logging.getLogger(__name__)


class IrcProtocol():
    """ This class defines functions to send messages over the IRC protocol
        in order to make more of a black box. It currently expects self.sock and self.config to be valid.. """
    invalid_chars = bytes.maketrans(bytes(string.ascii_lowercase, 'ascii'), b' ' * len(string.ascii_lowercase))

    def __init__(self):
        return

    @staticmethod
    def wrap_ctcp(message):
        return "\x01{0}\x01".format(message)

    @staticmethod
    def notice(destination, message):
        return "NOTICE {0} :{1}".format(destination, message)

    @staticmethod
    def privmsg(destination, message):
        if message is "" or message is None:
            return None
        return "PRIVMSG {0} :{1}".format(destination, message)

    @staticmethod
    def nick(nick):
        return "NICK {0}".format(nick)

    @staticmethod
    def user(user, unused, owner):
        return "USER {0} {1} {2} {3}".format(user, 0, unused, owner)

    @staticmethod
    def mode(nick, mode):
        return "MODE {0} {1}".format(nick, mode)

    @staticmethod
    def join(channel):
        return "JOIN {0}".format(channel)

    @staticmethod
    def part(channel, message="Leaving"):
        return "PART {0} {1}".format(channel, message)

    @staticmethod
    def quit(quit_message="Quitting"):
        return "QUIT :{0}".format(quit_message)

    # This is a bot, make sure you use your email!
    @staticmethod
    def register(owner_email, password):
        return IrcProtocol.privmsg("NICKSERV",
                                   "REGISTER {0} {1}".format(owner_email,
                                                             password))

    @staticmethod
    def identify(password):
        return IrcProtocol.privmsg("NICKSERV",
                                   "IDENTIFY {0}".format(password))

    @staticmethod
    def ping(destination, timestamp):
        message = IrcProtocol.wrap_ctcp("PING")
        return IrcProtocol.privmsg(destination, message)

    # Utility Functions
    @staticmethod
    def server_pong(string):
        return "PONG {0}".format(string)

    @staticmethod
    def scrub(message):
        return message.translate(None, IrcProtocol.invalid_chars)

    @staticmethod
    def split_message(message):
        prefix, commands, parameters = None, None, None

        if message[0] == ':':
            prefix, msg = message.split(' ', 1)

            if ' ' in msg:
                command, parameters = msg.split(' ', 1)
            else:
                command = msg
        else:
            command, parameters = message.split(' ', 1)

        return prefix, command, parameters

    @staticmethod
    def parse_prefix(prefix):
        sender, user, ident = None, None, None

        if prefix is not None:
            if '!' in prefix:
                sender = prefix.split('!')[0][1:]
                ident = prefix.split('!')[1]

                if '@' in ident:
                    user, ident = ident.split('@')
            else:
                sender = prefix
                ident = prefix

        return sender, user, ident
