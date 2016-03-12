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
import datetime
import string


logger = logging.getLogger(__name__)


class IrcProtocol:
    """ This class defines functions to send messages over the IRC protocol
        in order to make more of a black box. It currently expects self.sock and self.config to be valid.. """
    def __init__(self):
        self.sock = None

        self.invalid_chars = string.maketrans(string.ascii_lowercase, ' ' * len(string.ascii_lowercase))

    def _msg(self, message):
        """ Send a basic IRC message over the socket."""
        self.sock.send("{0}\r\n".format(message))
        message = re.sub("NICKSERV :(.*) .*", "NICKSERV :\g<1> <password>", message)
        print message

    def wrap_ctcp(self, message):
        return "\x01{0}\x01".format(message)

    def notice(self, destination, message):
        self._msg("NOTICE {0} :{1}".format(destination, message))

    def privmsg(self, destination, message):
        if message is "" or message is None:
            return
        self._msg("PRIVMSG {0} :{1}".format(destination, message))

    def nick(self, nick):
        self._msg("NICK {0}".format(nick))

    def user(self, user, unused, owner):
        self._msg("USER {0} {1} {2} {3}".format(user, 0, unused, owner))

    def mode(self, nick, mode):
        self._msg("MODE {0} {1}".format(nick, mode))

    def join(self, channel):
        self._msg("JOIN {0}".format(channel))

    def part(self, channel, message="Leaving"):
        self._msg("PART {0} {1}".format(channel, message))

    def quit(self, quit_msg="Quitting"):
        self._msg("QUIT :{0}".format(quit_msg))

    def register(self, owner_email, password):
        self.privmsg("NICKSERV", "REGISTER {0} {1}".format(owner_email, password))

    def identify(self, password):
        self.privmsg("NICKSERV", "IDENTIFY {0}".format(password))

    def ping(self, destination, timestamp):
        msg = self.wrap_ctcp("PING")
        self.privmsg(destination, msg)

    # Utility Functions
    def scrub(self, message):
        return message.translate(None, self.invalid_chars)

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

        return sender, ident

