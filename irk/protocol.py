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

from utils import pretty, timestamp


logger = logging.getLogger(__name__)


class IrcProtocol:
    def __init__(self):
        self.sock = None
        self.config = None

    # IRC Messages
    def _msg(self, message):
        self.sock.send("{0}\r\n".format(message))
        message = re.sub("NICKSERV :(.*) .*", "NICKSERV :\g<1> <password>", message)
        logger.info(pretty(message, 'SEND'))

    def _wrap_ctcp(self, message, destination=None):
        if destination is not None:
            return destination, "\x01{0}\x01".format(message)
        else:
            return "\x01{0}\x01".format(message)

    def notice(self, destination, message):
        self._msg("NOTICE {0} :{1}".format(destination, message))

    def privmsg(self, destination, message):
        if message is "" or message is None:
            return
        self._msg("PRIVMSG {0} :{1}".format(destination, message))

    def nick(self):
        self._msg("NICK {0}".format(self.config['nick']))

    def user(self):
        self._msg("USER {0} {1} {2} {3}".format(self.config['user'], 0, self.config['unused'], self.config['owner']))

    def mode(self):
        self._msg("MODE {0} {1}".format(self.config['nick'], self.config['mode']))

    def join(self, channel):
        self._msg("JOIN {0}".format(channel))

    def part(self, channel, message="Leaving"):
        self._msg("PART {0} {1}".format(channel, message))

    def quit(self, quit_msg='Quitting'):
        self._msg("QUIT :{0}".format(quit_msg))

    def register(self):
        self.privmsg("NICKSERV", "REGISTER {0} {1}".format(self.config['owner_email'], self.config['pass']))

    def identify(self):
        self.privmsg("NICKSERV", "IDENTIFY {0}".format(self.config['pass']))

    def privmsg_ping(self, destination):
        # self.waitingforpong = True, then in loop if self, etc to time
        time = str(timestamp())
        msg = "\x01PING {0} {1}\x01".format(time[:10], time[10:])
        self.privmsg(destination, msg)

    def notice_ping(self, destination, params):
        self.notice(destination, "\x01PING {0}\x01".format(params))
