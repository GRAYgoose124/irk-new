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
import os

from plugin import PluginManager
from ircclient import IrcClient
from utils import pretty

logger = logging.getLogger(__name__)

# TODO: Plugins
# TODO: Dict/Hash efficient lookup

class IrcBot(IrcClient, PluginManager):
    def __init__(self, directory, config, interactive=True):
        IrcClient.__init__(self, directory, config, interactive)
        PluginManager.__init__(self)

        plugin_folder = os.path.join(directory, "plugins")
        self.load_plugin_folder(plugin_folder)
        # get host if owner && if he's identified
        self.logged_in_host = None

    def proc_notice(self, sender, prefix, params):
        return

    # make this take channel/query dest as well
    def proc_privmsg(self, data):
        logger.debug(pretty("%s %s %s %s %s"), *data)
        sender_nick, hostname, destination, command, params = data
        # SORT data into queries and channels
        # Put into dict/hash O(n) search...
        # TODO: Yield data to bot so the bot can asyncronously process it
        # TODO: Offload to Bot class. Add more commands. (privileges,etc) (in plugins)
        # We need to be sure it's actually a command at this point..
        if sender_nick == self.config['owner']:
            if command  ==  '!quit':
                self.quit()
            elif command == '!join':
                if str(params[0])[0] == '#':
                    self.join(str(params[0]))
            elif command == '!part':
                if str(params[0])[0] == '#':
                    self.part(str(params[0]))
            elif command == '!ping':
                self.privmsg_ping(sender_nick)
            
            self.privmsg_plugin_hooks(data)

            if command[0] == '!':
                logger.info(pretty("{0} ran {1}".format(sender_nick, command), 'BOT'))
