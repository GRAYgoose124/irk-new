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


class IrcProtocol(QtCore.QObject):
    """ This class defines functions to send messages over the IRC protocol
        in order to make more of a black box. It currently expects self.sock and self.config to be valid.. """
    chat_update = QtCore.pyqtSignal(str)
    def __init__(self):
        QtCore.QObject.__init__(self)

        self.sock = None
        self.invalid_chars = bytes.maketrans(bytes(string.ascii_lowercase, 'ascii'), b' ' * len(string.ascii_lowercase))

    def __msg(self, message, limit=512):
        """ Send a basic IRC message over the socket."""
        if len(message) >= (limit - 2):
            message = message[:limit - 2]

        self.sock.send(bytes("{0}\r\n".format(message), 'ascii'))
        message = re.sub("NICKSERV :(.*) .*", "NICKSERV :\g<1> <password>", message)

        self.chat_update.emit(message)

    def wrap_ctcp(self, message):
        return "\x01{0}\x01".format(message)

    def notice(self, destination, message):
        self.__msg("NOTICE {0} :{1}".format(destination, message))

    def privmsg(self, destination, message):
        if message is "" or message is None:
            return
        self.__msg("PRIVMSG {0} :{1}".format(destination, message))

    def nick(self, nick):
        self.__msg("NICK {0}".format(nick))

    def user(self, user, unused, owner):
        self.__msg("USER {0} {1} {2} {3}".format(user, 0, unused, owner))

    def mode(self, nick, mode):
        self.__msg("MODE {0} {1}".format(nick, mode))

    def join(self, channel):
        self.__msg("JOIN {0}".format(channel))

    def part(self, channel, message="Leaving"):
        self.__msg("PART {0} {1}".format(channel, message))

    def quit(self, quit_msg="Quitting"):
        self.__msg("QUIT :{0}".format(quit_msg))

    def register(self, owner_email, password):
        self.privmsg("NICKSERV", "REGISTER {0} {1}".format(owner_email, password))

    def identify(self, password):
        self.privmsg("NICKSERV", "IDENTIFY {0}".format(password))

    def ping(self, destination, timestamp):
        msg = self.wrap_ctcp("PING")
        self.privmsg(destination, msg)

    # Utility Functions
    def server_pong(self, string):
        self.__msg("PONG {0}".format(string))
    def scrub(self, message):
        return message.translate(None, self.invalid_chars)

    # Todo: Rename params to message
    def split_message(self, message):
        prefix, commands, params = None, None, None

        if message[0] == ':':
            prefix, msg = message.split(' ', 1)

            if ' ' in msg:
                command, params = msg.split(' ', 1)
            else:
                command = msg
        else:
            command, params = message.split(' ', 1)

        return prefix, command, params

    def parse_prefix(self, prefix):
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

        return sender, ident
