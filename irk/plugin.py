import ircbot
from utils import pretty

import os
import re
import json
import imp
import logging

#from utils import cwdopen


logger = logging.getLogger(__name__)

class PluginManager:
    def __init__(self):
        self.plugins = []

    def load_plugin_folder(self, folder_name):
        plugin = None
        if os.path.isabs(folder_name):
            for (_, _, filenames) in os.walk(folder_name):
                for filename in filenames:
                    python_file = os.path.join(folder_name, filename)
                    if re.match("[a-zA-Z]+\.pyc", filename):
                        plugin = imp.load_compiled(filename, python_file)
                        self.plugins.append(plugin)
                    elif re.match("[a-zA-Z]+\.py", filename):
                        plugin = imp.load_source(filename, python_file)
                        self.plugins.append(plugin)
        else:
            raise ValueError("Not an absolute pathname!")

    def reload_plugin(self, plugin_name):
        for plugin in self.plugins:
            if plugin.__name__ == plugin_name:
                reload(self.plugins)
                return

    def list_plugins(self):
        print self.plugins

    def privmsg_hooks(self, data):
        logger.debug("PRIVMSG HOOKING")
        for plugin in self.plugins:
            try:
                plugin.process_privmsg(data)
            except NotImplemented:
                logger.debug("%s doesn't implement process_privmsg()", plugin.__name__)


# Plugin requirements:
# dependent_plugins
#
class Plugin():
    def __init__(self, PluginManager, plugin_folder):
        self.PM = PluginManager
        self.plugin_name = os.path.split(plugin_folder)[-1:]

        manifest_file = os.path.join(plugin_folder, self.plugin_name)
        self.manifest = json.load(open(manifest_file))

        python_file = os.path.join(plugin_folder, self.plugin_name + ".py")
        self.plugin = imp.load_source(self.plugin_name, python_file)

    def process_privmsg(self, data):
        raise NotImplemented('Plugin.process_privmsg() not implemented.')

