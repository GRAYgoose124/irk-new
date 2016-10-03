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

from plugin import Plugin


logger = logging.getLogger(__name__)


class Log(Plugin):
    def __init__(self, handler):
        super().__init__(handler)
        self.commands = {
        }

        self.logs = {}

        self.log_file_location = os.path.join(handler.config['home_path'], "logs")
        if not os.path.exists(self.log_file_location):
            os.mkdir(self.log_file_location)

    def send_privmsg_hook(self, *event):
        self.privmsg_hook(*event)

    def privmsg_hook(self, *event):
        _, data = event
        message = data[0]
        sender = data[1]
        original_dest = data[2]

        if original_dest not in self.logs:
            self.logs[original_dest] = "{}> {}\n".format(sender, message)
        else:
            self.logs[original_dest] += "{}> {}\n".format(sender, message)

    def server_ping_hook(self, *event):
        self.stop_hook()

    def stop_hook(self, *event):
        for channel, log in self.logs.items():
            log_file = os.path.join(self.log_file_location, "{}.txt".format(channel))
            with open(log_file, 'a') as f:
                logger.info("Log written: {}".format(channel))
                f.write(log)
            self.logs = { }
