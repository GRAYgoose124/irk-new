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
import logging


logger = logging.getLogger(__name__)


class Irc:
    """
    This class provides IRC message format functions.
    These functions return a message ready to send.

    It also provides basic IRC utility functions.
    """

    # Message Utility Functions
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
    def split_prefix(prefix):
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

    @staticmethod
    def wrap_ctcp(message):
        return "\x01{}\x01".format(message)

    # Basic IRC Messages
    @staticmethod
    def notice(destination, message):
        return "NOTICE {} :{}".format(destination, message)

    @staticmethod
    def privmsg(destination, message):
        if message is "" or message is None:
            return None
        return "PRIVMSG {} :{}".format(destination, message)

    @staticmethod
    def nick(nick):
        return "NICK {}".format(nick)

    @staticmethod
    def user(user, unused, owner):
        return "USER {} {} {} {}".format(user, 0, unused, owner)

    @staticmethod
    def mode(nick, mode):
        return "MODE {} {}".format(nick, mode)

    @staticmethod
    def join(channel):
        return "JOIN {}".format(channel)

    @staticmethod
    def part(channel, message="Leaving"):
        return "PART {} {}".format(channel, message)

    @staticmethod
    def quit(quit_message="Quitting"):
        return "QUIT :{}".format(quit_message)

    # NICKSERV messages
    @staticmethod
    def register(owner_email, password):
        return Irc.privmsg("NICKSERV",
                           "REGISTER {} {}".format(owner_email, password))

    @staticmethod
    def identify(password):
        return Irc.privmsg("NICKSERV",
                           "IDENTIFY {}".format(password))

    # Special Messages
    @staticmethod
    def server_pong(message):
        """
        This should be used to respond to a server PING.
        The server PING comes with data that should be
        echoed in the PONG."""
        return "PONG {}".format(message)

    @staticmethod
    def ctcp_ping(destination, timestamp):
        """
        This is a CTCP ping sent to a destination and
        the expected response is a ctcp_pong with the
        same timestamp. The time delta from the ctcp_ping
        and the expected ctcp_pong gives an estimate travel
        time.
        """
        message = Irc.wrap_ctcp("PING {}".format(timestamp))
        return Irc.privmsg(destination, message)

    @staticmethod
    def ctcp_pong(destination, timestamp):
        """
        This is used to respond to ctcp_pings.
        """
        message = Irc.wrap_ctcp("PING {}".format(timestamp))
        return Irc.notice(destination, message)




