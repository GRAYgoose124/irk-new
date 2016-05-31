import os
# TODO: Update to importlib
import imp
import logging


logger = logging.getLogger(__name__)

class PluginManager:
    def __init__(self, folder_name):
        self.plugins = []
        self.plugins_folder = None

        self.load_plugins_folder(folder_name)

    def load_plugins_folder(self, folder_name):
        self.plugins_folder = folder_name

        if os.path.isabs(folder_name):
            for (_, _, filenames) in os.walk(folder_name):
                for filename in filenames:
                    plugin_name, file_ext = os.path.splitext(filename)
                    if file_ext == ".py":
                        self.load_plugin_file(plugin_name)
        else:
            raise ValueError("Not an absolute pathname!")

        logger.info("Loaded plugins: %s", self.plugins)

    def load_plugin_file(self, plugin_name):
        plugin = None
        python_file = os.path.join(self.plugins_folder, plugin_name + ".py")

        if os.path.isfile(python_file):
            try:
                plugin = imp.load_source(plugin_name, python_file)
            except Exception as e:
                logger.warning(repr(e))
                plugin = None

            if plugin:
                loaded_plugin = getattr(plugin, plugin_name)(self)
                for p in self.plugins:
                    if loaded_plugin.__class__.__name__ == p.__class__.__name__:
                        self.plugins.remove(p)

                self.plugins.append(loaded_plugin)

                logger.debug("%s", loaded_plugin)
                logger.debug("Plugin %s loaded.", plugin_name)
            else:
                logger.debug("Failed to load: %s", plugin)

        return plugin

    # TODO: Load whole package
    def load_plugin_package(self):
        pass
