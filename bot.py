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
import re
import threading
import time

from daemon import Daemon
from plugin import PluginManager


logger = logging.getLogger(__name__)


# TODO: get necessary items from client config (name, authorized user, etc)
default_bot_config = {
    'admin_pass': "",
    'name': "",
    'authorized_users': [],
    'plugin_path': "plugins"
}


class Bot(Daemon):
    def __init__(self, config):
        super().__init__()

        self.config = config

        self.plugin_manager = PluginManager(self, os.path.join(self.config['home_path'], self.config['plugin_path']))
        self.plugin_manager.load_plugins()

        self.builtin_commands = {
            'quit': self._quit,
            'join': self._join,
            'part': self._part,
            'loaded': self._plugin_loaded,
            'unload': self._plugin_unload,
            'load': self._plugin_load,
            'reload': self._plugin_reload,
            'ping': self._ping,
            'help': self._command_help
        }

        self.events = {
            'send_privmsg': self._send_privmsg_event,
            'privmsg': self._privmsg_event,
            'stop': self._stop_event,
            'pong': self._pong_event,
            'users': self._qnull_event,
            'part': self._part_event,
            'recv': self._qnull_event,
            'send': self._qnull_event,
            'server_ping': self._qnull_event,
            'join': self._qnull_event
        }
        self.channels = {}

    def init_loop(self):
        logger.info("Bot started.")

    def cleanup_loop(self):
        self.event_handler(("stop", ()))

    def do(self):
        #TODO: Event driven framework?
        time.sleep(0.01)

    def event_handler(self, event):
        event_type, data = event

        # TODO: Pool?
        try:
            for _, plugin in self.plugin_manager.plugins.items():
                try:
                    attr = getattr(plugin, "{}_hook".format(event_type))
                except AttributeError:
                    attr = None

                if attr is not None:
                    attr_thread = threading.Thread(target=attr, args=event)
                    attr_thread.start()

        except RuntimeError as e:
            logger.debug("Skipped plugin hooks. {}".format(e))

        self.events.get(event_type, self._null_event)(event)

    # Built-in commands
    @staticmethod
    def _null_command(data):
        logger.debug("Unknown command: {}".format(data))

    def _quit(self, data):
        message = data[0]
        sender = data[1]
        destination = data[2]

        if re.search(self.config['admin_pass'], message):
            self.send_event("stop", message)
            self.stop()
        else:
            self.send_event("send_response", "Fuck You!", sender)

    def _ping(self, data):
        self.send_event("ping", data)

    def _join(self, data):
        self.send_event("join", data)

    def _part(self, data):
        self.send_event("part", data)

    def _plugin_loaded(self, data):
        if data[2][0] == '#':
            destination = data[2]
        else:
            destination = data[1]

        self.send_event("send_response", "Loaded plugins: {}".format([i for i in self.plugin_manager.plugins.keys()]), destination)

    def _plugin_reload(self, data):
        try:
            plugin_name = data[0].split(" ")[2]
        except IndexError:
            plugin_name = None

        if plugin_name in self.plugin_manager.plugins:
            self._plugin_unload(data)
            self._plugin_load(data)

    def _plugin_unload(self, data):
        try:
            plugin_name = data[0].split(" ")[2]
        except IndexError:
            return

        if data[2][0] == '#':
            destination = data[2]
        else:
            destination = data[1]

        if plugin_name == "all":
            self.plugin_manager.unload_plugins()
            self.send_event("send_response", "All plugins unloaded.", destination)

        elif plugin_name in self.plugin_manager.plugins:
            self.plugin_manager.unload_plugin(plugin_name)
            self.send_event("send_response", "Plugin {} unloaded.".format(plugin_name), destination)

    def _plugin_load(self, data):
        try:
            plugin_name = data[0].split(" ")[2]
        except IndexError:
            return

        if data[2][0] == '#':
            destination = data[2]
        else:
            destination = data[1]
        if plugin_name == "all":
            self.plugin_manager.load_plugins()
            self.send_event("send_response", "All plugins loaded: {}".format([i for i in self.plugin_manager.plugins.keys()]),
                            destination)

        else:
            self.plugin_manager.load_plugin(plugin_name)
            self.send_event("send_response", "Plugin {} loaded.".format(plugin_name), destination)

    def _command_help(self, data):
        if data[2][0] == '#':
            destination = data[2]
        else:
            destination = data[1]

        cmds = [i for i in self.builtin_commands]
        self.send_event("send_response", cmds, destination)

        cmds = [i for i in self.plugin_manager.commands]
        self.send_event("send_response", cmds, destination)

    # Events
    def _privmsg_event(self, event):
        event_type, data = event
        message = data[0]
        sender = data[1]
        destination = data[2]

        tokens = message.split(" ")

        prefix, command, message = None, None, None
        if len(tokens) == 1:
            command = tokens[0]
        elif len(tokens) == 2:
            command, message = tokens
        elif len(tokens) >= 3:
            prefix = tokens[0]
            if not re.search("{}[:,]?".format(self.config['name']), prefix):
                command, *message = tokens
            else:
                command, *message = tokens[1:]

        if destination[0] == '#' and prefix is None:
            command, message = message, ""
            prefix = self.config['name']

        # TODO: Proper authentication
        if command is not None:
            if sender in self.config['authorized_users']:
                if prefix is None and destination != self.config['name']:
                    return

                if command in self.builtin_commands:
                    logger.debug("CMD | {}: {}".format(command, message))
                    self.builtin_commands.get(command, self._null_command)(data)
                elif command in self.plugin_manager.commands:
                    logger.debug("CMD | {}: {}".format(command, message))
                    # TODO: threading
                    plugin_thread = threading.Thread(target=self.plugin_manager.commands.get(command,
                                                                                             self._null_command),
                                                     args=data)
                    logger.log(level=5, msg=plugin_thread)
                    plugin_thread.start()
                else:
                    self._null_command(command)

    def _stop_event(self, event):
        self.stop()

    def _pong_event(self, event):
        event_type, data = event

        try:
            if data[2][0] == '#':
                destination = data[2]
            else:
                destination = data[1]
        except IndexError:
            destination = data[1]

        logger.info("Ping time: {}".format(data[0]))
        self.send_event("send_response", "Ping time: {}".format(data[0]), destination)

    def _part_event(self, event):
        event_type, data = event
        # self.channels.pop(data[0])

    def _send_privmsg_event(self, event):
        pass
