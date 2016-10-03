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
import os
import importlib.util


logger = logging.getLogger(__name__)


# <event>_hook(self, event) are event hook functions
# commands are added by putting them in dict
class Plugin:
    def __init__(self, handler):
        self.handler = handler
        self.commands = {}

    # Plugin API functions
    def send_message(self, message, destination):
        self.handler.send_event("send_response", message, destination)


class PluginManager:
    def __init__(self, handler, plugins_path):
        self.handler = handler
        self.plugins_path = plugins_path
        self.plugins = {}

        self.commands = {}

    # Manager functions
    def load_plugin(self, plugin_name):
        try:
            spec = importlib.util.spec_from_file_location(plugin_name,
                                                          os.path.join(self.plugins_path, "{}.py".format(plugin_name)))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        except Exception as e:
            logger.warn(e)
            return

        try:
            plugin = getattr(module, plugin_name)(self.handler)
        except AttributeError:
            logger.warn("Invalid Plugin: {}".format(plugin_name))
            return

        self.commands.update(plugin.commands)
        self.plugins[plugin_name] = plugin

    def unload_plugin(self, plugin_name):
        try:
            for key in self.plugins[plugin_name].commands:
                if key in self.commands:
                    self.commands.pop(key)

            self.plugins.pop(plugin_name)
        except KeyError:
            pass

    def load_plugins(self):
        for plugin_name in os.listdir(self.plugins_path):
            if plugin_name[-3:] == ".py" and plugin_name != "__init__.py":
                self.load_plugin(plugin_name[:-3])

    def unload_plugins(self):
        plugins_copy = self.plugins.copy()
        for plugin_name in plugins_copy:
            self.unload_plugin(plugin_name)


