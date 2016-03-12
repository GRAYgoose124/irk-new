#   Irk: irc bot
#   Copyright (C) 2016  Grayson Miller

#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.

#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.

#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>
import sys
import os
import json
import logging
import getpass

from bot import IrcBot


logging.addLevelName(25, "OUT")
logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)


def main():
    home_directory = ".irk"

    # TODO: Clean up logging levels and logging, remove extraneous and organize.
    # Logging
    format = logging.Formatter('[%(levelname)s:%(name)s] %(message)s')
    stream_handler = logging.StreamHandler(sys.stdout)
    logger.addHandler(stream_handler.setFormatter(format))

    log_filename = __name__ + "_debug.log"
    file_handler = logging.FileHandler(log_filename, 'w')
    logger.addHandler(file_handler.setFormatter(format))

    # Start Bot
    client = IrcBot(home_directory)
    try:
        client.start()
    except KeyboardInterrupt:
        client.stop()


if __name__ == '__main__':
    main()