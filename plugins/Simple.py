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
import time

from plugin import Plugin


logger = logging.getLogger(__name__)


class Simple(Plugin):
    def __init__(self, handler):
        super().__init__(handler)
        self.commands = {
            'test': self.test
        }

    def privmsg_hook(self, *event):
        logger.info("Simple Hook")

    def test(self, *data):
        logger.info("Simple Command")
