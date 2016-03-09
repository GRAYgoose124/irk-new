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
import logging
import sys

from ircclient import IrcClient

logger = logging.getLogger(__name__)

# TODO: Plugins
# TODO: Dict/Hash efficient lookup

class IrcBot(IrcClient):
    def __init__(self, directory, config, interactive=True):
        IrcClient.__init__(self, directory, config, interactive)

        # get host if owner && if he's identified
        self.logged_in_host = None

    def proc_notice(self, sender, prefix, params):
        return

    def proc_privmsg(self, sender, command, params):
        logger.debug("privmsg: %s %s %s", sender, command, params)
        # SORT data into queries and channels
        # Put into dict/hash O(n) search...
        # TODO: Yield data to bot so the bot can asyncronously process it.
        # TODO: Offload to Bot class. Add more commands. (privileges,etc) (in plugins)

        if sender[0] == self.config['owner']:
            if command  ==  '!quit':
                self.quit()
            elif command == '!join':
                if str(params[0])[0] == '#':
                    self.join(str(params[0]))
            elif command == '!ping':
                    self.privmsg_ping(sender[0])
