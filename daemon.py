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
import multiprocessing
import queue
import logging
import time
import pickle

logger = logging.getLogger(__name__)


class Daemon(multiprocessing.Process):
    def __init__(self, keep_alive=None):
        super().__init__()

        self.quit = True

        self.keep_alive = keep_alive
        if self.keep_alive is not None:
            self.keep_alive_until = time.clock() + self.keep_alive
        else:
            self.keep_alive_until = None

        self.input_queue = multiprocessing.Queue()
        self.output_queue = None

    # Events TODO: expand to multi-connection? Plugins are piggy backing. proper pickling and piping
    def connect_queues(self, d2):
        self.output_queue = d2.input_queue
        d2.output_queue = self.input_queue

    def send_event(self, etype, *data):
        logger.log(level=5, msg="{}: Sending event: {}".format(self.__class__, [etype, data]))
        packet = pickle.dumps([etype, data])
        self.output_queue.put(packet)

    def process_events(self):
        while True:
            try:
                event = self.input_queue.get(block=False)
                event = pickle.loads(event)
            except queue.Empty:
                break

            logger.log(level=5, msg="{}: Event caught: {} {}".format(self.__class__, *event))
            self.event_handler(event)

            if self.keep_alive is not None:
                self.keep_alive_until = time.clock() + self.keep_alive

    def event_handler(self, event):
        pass

    def _qnull_event(self, event):
        pass

    def _null_event(self, event):
        event_type, data = event
        event = event_type, data
        logger.debug("EVT | {}: Unknown event: {}".format(self.__class__, event))

    # Runtime
    def run(self):
        self.quit = False

        self.init_loop()
        self._loop()
        self.cleanup_loop()

        logger.debug("DMN | {} stopped.".format(self.__class__))

    def stop(self):
        self.quit = True

    def _loop(self):
        while not self.quit:
            self.do()
            self.process_events()

            if self.keep_alive is not None and time.clock() > self.keep_alive_until:
                logger.info("Stopping {}: Event timeout exceeded.".format(self.__class__))
                self.stop()

    def init_loop(self):
        pass

    def cleanup_loop(self):
        pass

    def do(self):
        raise NotImplementedError

