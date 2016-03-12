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
    def __init__(self, folder_name):
        self.plugins = []
        self.load_plugin_folder(folder_name)

    # Move parameter into __init__
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
                        plugin = None

        else:
            raise ValueError("Not an absolute pathname!")

        logger.debug(pretty("Loaded plugins: {0}".format(self.plugins)))

    def load_plugin(self, plugin_name):
        python_file = os.path.join(self.plugin_folder, plugin_name + ".py")

        if os.path.isfile(python_file):
            p = imp.load_source(plugin_name, python_file)

            if p:
                self.plugins.append(getattr(p, plugin_name)())
                logger.debug(pretty("Plugin {0} loaded.".format(plugin_name)))
                return True

        return False

    def reload_plugin(self, plugin_name):
        for idx, plugin in enumerate(self.plugins):
            if plugin.__class__.__name__ == plugin_name:
                python_file = os.path.join(self.plugin_folder, plugin_name + ".py")

                if os.path.isfile(python_file):
                    p = imp.load_source(plugin_name, python_file)

                    if p:
                        self.plugins[idx] = getattr(p, plugin_name)()
                        logger.debug(pretty("Plugin {0} reloaded.".format(plugin_name)))
                        return True
        return False

    def list_plugins(self):
        print self.plugins

    # TODO ADD hooks for all types of messages + parallelize, add to API
    def privmsg_plugin_hooks(self, data):
        for plugin in self.plugins:
            if hasattr(plugin, 'privmsg_hook'):
                logger.log(9, pretty("Running {0}.privmsg_hook()".format(plugin.__class__.__name__)))

                try:
                    plugin.privmsg_hook(self, data)
                except Exception as e:
                    # TODO: Unload plugin, report in chat.
                    logger.warning(pretty("Plugin {0}\n\t\t{1}".format(plugin.__class__.__name__, repr(e)), 'PLUGIN_ERROR'))
