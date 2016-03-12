import os
import imp
import logging


logger = logging.getLogger(__name__)


# TODO: Merge reused code and be verbose about plugin syntax errors.
class PluginManager:
    def __init__(self, folder_name):
        self.plugins = []
        self.load_plugin_folder(folder_name)

    def load_plugin_folder(self, folder_name):
        plugin = None
        self.plugin_folder = folder_name

        if os.path.isabs(folder_name):
            for (_, _, filenames) in os.walk(folder_name):
                for filename in filenames:
                    plugin_name, file_ext = os.path.splitext(filename)
                    python_file = os.path.join(folder_name, filename)

                    if file_ext == ".py":
                        try:
                            plugin = imp.load_source(plugin_name, python_file)
                        except:
                            plugin = None

                    if plugin:
                        if hasattr(plugin, plugin_name):
                            plugin_instance = getattr(plugin, plugin_name)()

                            if plugin_instance:
                                self.plugins.append(plugin_instance)
                                logger.info("Plugin %s loaded.", plugin_name)

                        plugin = None

        else:
            raise ValueError("Not an absolute pathname!")

        logger.debug("Loaded plugins: %s", self.plugins)

    def load_plugin(self, plugin_name):
        plugin = None
        python_file = os.path.join(self.plugin_folder, plugin_name + ".py")

        if os.path.isfile(python_file):
            try:
                plugin = imp.load_source(plugin_name, python_file)
            except:
                plugin = None

            if plugin:
                self.plugins.append(getattr(plugin, plugin_name)())
                logger.debug("Plugin %s loaded.", plugin_name)
                plugin = self.plugins[len(self.plugins)]

        return plugin

    def reload_plugin(self, plugin_name):
        plugin = None
        for idx, plugin in enumerate(self.plugins):
            if plugin.__class__.__name__ == plugin_name:
                python_file = os.path.join(self.plugin_folder, plugin_name + ".py")

                if os.path.isfile(python_file):
                    try:
                        plugin = imp.load_source(plugin_name, python_file)
                    except:
                        plugin = None

                    if plugin:
                        self.plugins[idx] = getattr(plugin, plugin_name)()
                        logger.debug("Plugin %s reloaded.", plugin_name)
                        plugin = self.plugins[idx]

        return plugin

    # TODO ADD hooks for all types of messages + parallelize, add to API
    def run_privmsg_hooks(self, data):
        for plugin in self.plugins:
            if hasattr(plugin, 'privmsg_hook'):
                logging.debug("Running %s.privmsg_hook()", plugin.__class__.__name__)
                try:
                    plugin.privmsg_hook(self, data)
                except Exception as e:
                    # TODO: Unload plugin, report in chat.
                    logger.warning("Plugin %s\n\t\t%s\n", plugin.__class__.__name__, repr(e))
