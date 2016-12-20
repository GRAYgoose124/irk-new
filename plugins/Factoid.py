import logging

from plugin import Plugin


logger = logging.getLogger(__name__)


class Factoid(Plugin):
    def __init__(self, handler):
        super().__init__(handler)
        self.commands = {

        }
