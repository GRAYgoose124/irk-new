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
#g
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>
import logging
import os
import re
import time
from PyQt5 import QtCore

from irk.plugin import PluginManager
from irk.client import IrcClient, init_irc_config
from irk.protocol import IrcProtocol

logger = logging.getLogger(__name__)


# Note: Why is the position of PluginManager/IrcClient important?
class IrcBot(PluginManager, IrcClient):
    def __init__(self, root_directory, config_filename="config"):
        if os.path.isabs(root_directory):
            home_folder = root_directory
        else:
            home_folder = os.path.join(os.path.expanduser('~'), root_directory)

        plugins_folder = os.path.join(home_folder, "plugins")
        config_full_filename = os.path.join(home_folder, config_filename)

        # TODO: Do proper file checks and creation.
        if not os.path.isdir(home_folder):
            os.makedirs(plugins_folder)
        elif not os.path.isdir(plugins_folder):
            os.mkdir(plugins_folder)

        config = init_irc_config(config_full_filename)

        # IrcBot's built-in commands
        self.command_dict = {
            'quit': self.__quit,
            'restart': self.__restart,
            'join': self.__join,
            'part': self.__part,
            'load': self.__plugin_load,
            'help': self.__command_help
        }

        IrcClient.__init__(self, config)
        PluginManager.__init__(self, plugins_folder)

        self.privmsg_event.connect(self.process_privmsg_event)
        self.__connect_plugins_hooks()

    def process_privmsg_event(self, data):
        # TODO: Command processing, Plugin Hooks
        logger.debug("Processing PRIVMSG event...\n\t\t%s", data)
        if data['sender'] == self.config['owner']:
            if re.match(self.config['nick'] + "[:,]", data['message']):
                tokens = data['message'].split(' ')
                data['message'] = ' '.join(tokens[1:])
                logger.debug("Command caught: (%s) : (%s)", tokens[1], tokens[2:])
                self.command_dict.get(tokens[1], self.__noop)(data)

    def __connect_plugins_hooks(self):
        for plugin in self.plugins:
            plugin.handler = self
            # TODO: Check if plugin has hook first
            self.privmsg_event.connect(plugin.privmsg_hook)
        pass

    # Built-in Bot commands
    def __quit(self, data):
        self.send_message(IrcProtocol.quit("Quitting on command!"))

    def __restart(self, data):
        self.stop()
        self.start()

    # TODO: reformat data['message']...Currently inserting bot name from ui input to hack the interface together..
    def __join(self, data):
        channel = data['message'].split(" ")[1]
        if channel[0] == '#':
            self.send_message(IrcProtocol.join(channel))

    def __part(self, data):
        channel = data['message'].split(" ")[1]
        if channel[0] == '#':
            # TODO: Fix to make Duckborg parted.
            self.send_message(IrcProtocol.part(channel))

    def __plugin_load(self, data):
        plugin_name = data['message'].split(" ")[1]
        if self.load_plugin_file(plugin_name) is not None:
            self.send_response(" ".join((plugin_name, "loaded.")), data['sender'], data['original_destination'])

    def __command_help(self, data):
        command_list = ""
        for k, v in self.command_dict.items():
            command_list = command_list + ", " + k

        if data['original_destination'] is not None:
            self.send_response(command_list, None, data['original_destination'])
        elif data['sender'] is not None:
            self.send_response(command_list, data['sender'])
        else:
            self.message_received.emit(command_list)

    @staticmethod
    def __noop(data):
        logger.debug("Noop ran: %s", data)
