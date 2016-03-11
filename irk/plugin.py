import ircbot
from utils import pretty

import os
import re
import json
import imp
import logging

#from utils import cwdopen


logger = logging.getLogger(__name__)


class Plugin:
    def __init__(self, manager):
        self.manager = manager

    #def command_hook(self, data):
    #    raise NotImplementedError("".join(self.__class__.__name__))


class PluginManager:
    def __init__(self):
        self.plugins = []

    def load_plugin_folder(self, folder_name):
        if os.path.isabs(folder_name):
            for (_, _, filenames) in os.walk(folder_name):
                for filename in filenames:
                    plugin_name, file_ext = os.path.splitext(filename)
                    python_file = os.path.join(folder_name, filename)
                    if re.match("[a-zA-Z]+\.py.", filename):
                        if file_ext == ".py":
                            plugin = imp.load_source(plugin_name, python_file)   
                        elif file_ext == ".pyc":
                            plugin = imp.load_compiled(plugin_name, python_file)
                        else:
                            plugin = None
                        logger.debug("Plugin %s %s", plugin, plugin_name)
                        if plugin is not None:
                            if hasattr(plugin, plugin_name):
                                # Get an instance and become it's manager
                                plugin_instance = getattr(plugin, plugin_name)(self)
                                self.plugins.append(plugin_instance)
        else:
            raise ValueError("Not an absolute pathname!")

    def reload_plugin(self, plugin_name):
        for plugin in self.plugins:
            if plugin.__name__ == plugin_name:
                #reload(self.plugins)
                return

    def list_plugins(self):
        print self.plugins

    def privmsg_plugin_hooks(self, data):
        logger.debug("Processing privmsg plugin hooks.")
        for plugin in self.plugins:
            if hasattr(plugin, 'command_hook'):
                logger.debug("Running %s.command_hook()", plugin.__class__.__name__)
                plugin.command_hook(data)
