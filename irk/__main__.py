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
import logging

from bot import IrcBot


logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] %(name)s:%(lineno)s | %(message)s')
logger = logging.getLogger(__name__)


def main():
    home_directory = ".irk"

    client = IrcBot(home_directory)
    try:
        client.start()
    except KeyboardInterrupt:
        client.stop()

if __name__ == '__main__':
    main()