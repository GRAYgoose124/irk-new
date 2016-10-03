#!/bin/bash python3
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

import config
from bot import Bot, default_bot_config
from client import Client, default_client_config


__author__ = "Grayson Miller"
__version__ = "0.2.0"


logging.basicConfig(level=logging.DEBUG, format='[%(levelname)7s] %(name)7s:%(lineno)4s | %(message)s')
logger = logging.getLogger(__name__)


def main():
    # Handle configurations
    home_path = os.path.join(os.path.expanduser("~"), ".irk")
    config_path = os.path.join(home_path, "config")

    client_config_file = os.path.join(config_path, "client.conf")
    bot_config_file = os.path.join(config_path, "bot.conf")

    if not os.path.exists(home_path):
        os.mkdir(home_path)

    if not os.path.exists(config_path):
        os.mkdir(config_path)

    if not os.path.exists(client_config_file):
        client_config = config.interactive_build_config(default_client_config)
        config.save_config(client_config_file, client_config)
    else:
        client_config = config.load_config(client_config_file)

    if not os.path.exists(bot_config_file):
        bot_config = config.interactive_build_config(default_bot_config)
        config.save_config(bot_config_file, bot_config)
    else:
        bot_config = config.load_config(bot_config_file)

    # Retroactively patch home_path into configurations.
    client_config['home_path'] = home_path
    bot_config['home_path'] = home_path

    client_proc = Client(client_config)
    bot_proc = Bot(bot_config)
    client_proc.connect_queues(bot_proc)

    client_proc.start()
    bot_proc.start()

    client_proc.join()
    bot_proc.join()

if __name__ == '__main__':
    main()
