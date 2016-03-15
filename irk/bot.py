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
import os

from plugin import PluginManager
from client import IrcClient


logger = logging.getLogger(__name__)


class IrcBot(IrcClient, PluginManager):
    def __init__(self, home_directory):
        # Put it in the user's home if the path is ambiguous.
        if os.path.isabs(home_directory):
            self.home_directory = home_directory
        else:
            self.home_directory = os.path.join(os.path.expanduser('~'), home_directory)

        self.plugins_folder = os.path.join(self.home_directory, "plugins")

        # TODO: Do proper file checks and creation.
        if not os.path.isdir(self.home_directory):
            os.makedirs(self.plugins_folder)
        elif not os.path.isdir(self.plugins_folder):
            os.mkdir(self.plugins_folder)

        IrcClient.__init__(self, self.home_directory)
        PluginManager.__init__(self, self.plugins_folder)

        # TODO: API Documentation of IrcBot built-in commands
        self.command_dict = {
            'quit': self.quit,
            'reconnect': self.reconnect,
            'join': self.bot_join,
            'part': self.bot_part,
            'load': self.bot_plugin_load
         }

    # Process all PRIVMSG related events, these hooks
    def process_privmsg_events(self, data):
        # TODO: More robust 'login'/privilege system
        if data['sender'] == self.config['owner']:
            # IRC channels are usually prefixed with '#'
            # This assumption may be invalid, but I don't care at the moment.
            if data['orig_dest'][0] == '#':
                data['to_channel'] = True
            else:
                data['to_channel'] = False

            # TODO: Commands are restricted right now, no spaces allowed.
            command = None
            if data['command'] == self.config['nick']:
                command = data['command'] + data['argument'][0]


            self.command_dict.get(command, self.run_privmsg_hooks)(data)

    # TODO: Make more intelligent. This should be documented in API
    # Plugin Handler Functions
    def send_results(self, message, original_sender, destination=None):
        if destination[0] == '#' :
            self.privmsg(destination, message)
        else:
            self.privmsg(original_sender, message)

    # Built-in Bot commands TODO: Add to API
    def reconnect(self):
        self.quit()
        self.stop()
        self.start()

    def bot_join(self, data):
        if str(data['arguments'][0])[0] == '#':
            self.join(str(data['arguments'][0]))

    def bot_part(self, data):
        if str(data['arguments'][0])[0] == '#':
            self.part(str(data['arguments'][0]))

    def bot_plugin_load(self, data):
        plugin_name = str(data['arguments'][0])
        if self.load_plugin_file(plugin_name) is not None:
            self.send_results(" ".join((plugin_name, "loaded.")), data['sender'], data['orig_dest'])