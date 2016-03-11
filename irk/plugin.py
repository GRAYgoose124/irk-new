import bot
from utils import pretty

import os
import re
import json
import imp
import logging

from utils import pretty

import inspect

logger = logging.getLogger(__name__)


class PluginManager:
    def __init__(self):
        self.plugins = []
        self.plugin_folder = None

    # Move into __init__
    def load_plugin_folder(self, folder_name):
        plugin = None
        self.plugin_folder = folder_name
        if os.path.isabs(folder_name):
            for (_, _, filenames) in os.walk(folder_name):
                for filename in filenames:
                    plugin_name, file_ext = os.path.splitext(filename)
                    python_file = os.path.join(folder_name, filename)

                    if file_ext == ".py":
                        plugin = imp.load_source(plugin_name, python_file)

                    if plugin:
                        if hasattr(plugin, plugin_name):
                            # Get an instance and become it's manager
                            plugin_instance = getattr(plugin, plugin_name)()
                            if plugin_instance:
                                self.plugins.append(plugin_instance)
                                logger.info(pretty("Plugin {0} loaded.".format(plugin_name)))
        else:
            raise ValueError("Not an absolute pathname!")
        logger.debug(pretty("Loaded plugins: {0}".format(self.plugins)))

    # Move into init
    def reload_plugin(self, plugin_name):
        for idx, plugin in enumerate(self.plugins):
            if plugin.__class__.__name__ == plugin_name:
                python_file = os.path.join(self.plugin_folder, plugin_name + ".py")
                p = imp.load_source(plugin_name, python_file)
                if p:
                    self.plugins[idx] = getattr(p, plugin_name)()
                    logger.debug(pretty("Plugin {0} reloaded.".format(plugin_name)))

    def list_plugins(self):
        print self.plugins

    def privmsg_plugin_hooks(self, data):
        for plugin in self.plugins:
            if hasattr(plugin, 'command_hook'):
                logger.debug(pretty("Running {0}.command_hook()".format(plugin.__class__.__name__)))
                plugin.command_hook(self, data)
