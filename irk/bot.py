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
from utils import pretty


logger = logging.getLogger(__name__)


class IrcBot(IrcClient, PluginManager):
    def __init__(self, home_directory):
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

    # Process all PRIVMSG related event
    def process_privmsg_hooks(self, data):
        # TODO: More robust 'login'/privilege system
        if data['sender'] == self.config['owner']:

            if data['orig_dest'][0] == '#':
                data['to_channel'] = True
            else:
                data['to_channel'] = False

            if data['command']  ==  '!quit':
                self.quit()

            elif data['command'] == '!join':
                if str(data['arguments'][0])[0] == '#':
                    self.join(str(data['arguments'][0]))

            elif data['command'] == '!part':
                if str(data['arguments'][0])[0] == '#':
                    self.part(str(data['arguments'][0]))

            elif data['command'] == '!load':
                if self.load_plugin(str(data['arguments'][0])):
                    self.send_results(data)
            elif data['command'] == '!reload':
                if self.reload_plugin(str(data['arguments'][0])):
                    self.send_results(data)

            elif data['command'] == '!ping':
                self.privmsg_ping(data['sender'])

            # TODO: Create permissions, allow plugins to use other plugins, etc.
            # Run all PRIVMSG event hooks from plugins.

            self.privmsg_plugin_hooks(data)

            if data['command'][0] == '!':
                logger.debug(pretty("{0} ran {1}".format(data['sender'], data['command']), 'BOT'))

    # TODO: Make this more intelligent,
    def send_results(self, data):
        if data['orig_dest'] != self.config['nick']:
            self.privmsg(data['orig_dest'], "{} loaded.".format(data['arguments'][0]))
        else:
            self.privmsg(data['sender'], "{} loaded.".format(data['arguments'][0]))
