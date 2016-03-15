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
import os
import imp
import logging


logger = logging.getLogger(__name__)

# Plugin API data packet.
# data['sender']
# data['ident']
# data['orig_dest']
# data['command']
# data['arguments']
# data['to_channel']


# TODO: Merge reused code and be verbose about plugin syntax errors.
# TODO: Fix dumb load, load whole packages, etc
class PluginManager():
    def __init__(self, folder_name):
        self.plugins = []
        self.plugin_folder = None
        self.load_plugin_folder(folder_name)

    def load_plugin_folder(self, folder_name):
        self.plugin_folder = folder_name

        if os.path.isabs(folder_name):
            for (_, _, filenames) in os.walk(folder_name):
                for filename in filenames:
                    plugin_name, file_ext = os.path.splitext(filename)
                    if file_ext == ".py":
                        self.load_plugin_file(plugin_name)
        else:
            raise ValueError("Not an absolute pathname!")

        logger.debug("Loaded plugins: %s", self.plugins)

    def load_plugin_file(self, plugin_name):
        plugin = None
        python_file = os.path.join(self.plugin_folder, plugin_name + ".py")

        if os.path.isfile(python_file):
            try:
                plugin = imp.load_source(plugin_name, python_file)
            except Exception as e:
                logger.warning(repr(e))
                plugin = None

            if plugin:
                loaded_plugin = getattr(plugin, plugin_name)()
                for p in self.plugins:
                    if loaded_plugin.__class__.__name__ == p.__class__.__name__:
                        self.plugins.remove(p)

                self.plugins.append(loaded_plugin)

                logger.debug("Plugin %s loaded.", plugin_name)

        return plugin

    # TODO ADD hooks for all types of messages + parallelize, add to API
    # All Plugin Hooks
    def run_privmsg_hooks(self, data):
        for plugin in self.plugins:
            if hasattr(plugin, 'privmsg_hook'):
                logging.debug("Running %s.privmsg_hook()", plugin.__class__.__name__)
                try:
                    plugin.privmsg_hook(self, data)
                except Exception as e:
                    # TODO: Unload plugin, report in chat.
                    logger.warning("Plugin %s\n\t\t%s\n", plugin.__class__.__name__, repr(e))