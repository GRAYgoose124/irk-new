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
import socket
import ssl
import time
import re
import datetime

from daemon import Daemon
from irc import Irc


logger = logging.getLogger(__name__)


default_client_config = {
    'host': '', 'port': 7001, 'ipv6': False, 'ssl': True,
    'nick': '', 'pass': '',
    'ident': '', 'user': '',
    'mode': '+B', 'unused': '*',
    'owner': '', 'owner_email': '',
    'channels': []
}


class Client(Daemon):
    def __init__(self, config):
        super().__init__()

        self.sock = None
        self.config = config

        self.users = {}
        self.channels = []

        self.irc_events = {
            'PRIVMSG': self._handle_privmsg,
            'NOTICE': self._handle_notice,
            'JOIN': self._handle_join,
            'PART': self._handle_part,
            '001': self._set_mode,
            '332': self._qno_handle,
            '353': self._handle_userlist_update,
            '366': self._qno_handle,
            '376': self._handle_identify,
            '433': self._handle_433,
            'MODE': self._handle_mode,
            'PING': self._handle_server_ping,
        }

        self.events = {
            'ping': self._ping_event,
            'send_response': self._send_response_event,
            'stop': self._stop_event,
            'join': self._join_event,
            'part': self._part_event
        }

    def do(self):
        if self.sock is not None:
            try:
                data = self.sock.recv(2048)
            except socket.timeout:
                data = None
            except socket.error:
                logger.info("Socket error. Connection closed.")
                self.stop()
                return

            # IRC RFC2812:2.3
            if data is not None:
                messages = data.split(b'\r\n')
                for message in messages:
                    if message:
                        logger.info("--> | " + message.decode("utf-8"))
                        self._process_message(message)

    def event_handler(self, event):
        event_type, data = event
        self.events.get(event_type, self._null_event)(event)

    def init_loop(self):
        logger.info("Client started.")

        if self._init_socket() is not None:
            if self.config['ssl']:
                ssl_info = self.sock.cipher()
                if ssl_info:
                    logger.info("SSL Cipher (%s), SSL Version (%s), SSL Bits (%s)", *ssl_info)

            # IRC RFC2812:3.1 states that a client needs to send a nick and
            # user message in order to register a connection.
            # Most servers mandate that the user's real name be the owner.
            self._send_message(Irc.nick(self.config['nick']))
            self._send_message(Irc.user(self.config['user'], self.config['unused'], self.config['owner']))

        else:
            self.stop()

    def cleanup_loop(self):
        if self.sock is not None:
            self._send_message(Irc.quit("Quitting :)"))
            self.sock.close()
            self.sock = None

    def _init_socket(self):
        if self.config['ipv6']:
            sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0)
        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if sock is not None:
            if self.config['ssl']:
                self.sock = ssl.wrap_socket(sock)
            else:
                self.sock = sock

            try:
                self.sock.connect((self.config['host'], self.config['port']))

                self.sock.settimeout(0.01)
            except socket.gaierror as e:
                logger.error(e)

        logger.info("Client connected to {}".format(self.config['host']))
        return sock

    def _send_response(self, message, original_sender=None, destination=None):
        """ Sends a response to the correct location, whether a channel or query"""
        if destination is not None and destination[0] == '#' and message is not None:
            msg = Irc.privmsg(destination, message)
            self._send_message(msg)
            self.send_event("send_privmsg", str(message), self.config['nick'], destination)

        elif original_sender is not None and message is not None:
            msg = Irc.privmsg(original_sender, message)
            self._send_message(msg)
            self.send_event("send_privmsg", str(message), self.config['nick'], original_sender)

    def _send_message(self, message, limit=512):
        """ Send a basic IRC message over the socket."""
        if len(message) >= (limit - 2):
            message = message[:limit - 2]

        if self.sock is not None:
            logger.info("<-- | " + message)
            self.sock.send(bytes("{0}\r\n".format(message), 'ascii'))
            self.send_event("send", message)

        else:
            logger.debug("Tried to send message without a socket! message(%s)", message)
            message = None

        return message

    def _process_message(self, message):
        """Process IRC messages."""
        message = message.decode('ascii')
        # self.send_event("recv", message)

        _, command, _ = Irc.split_message(message)
        self.irc_events.get(command, self._no_handle)(message)

    # IRC Events
    def _qno_handle(self, message):
        pass

    @staticmethod
    def _no_handle(message):
        _, command, _ = Irc.split_message(message)
        logger.log(level=5, msg="Unknown IRC command: {}".format(command))

    def _handle_privmsg(self, message):
        prefix, command, parameters = Irc.split_message(message)
        sender, user, ident = Irc.split_prefix(prefix)

        channel, msg = parameters.split(" ", 1)
        self.send_event("privmsg", msg[1:], sender, channel)

        if prefix is None:
            logger.debug("Malformed PRIVMSG: %s", message)
            return

        tokens = parameters.split(' ')
        privmsg_command = tokens[1][1:]

        message = privmsg_command + " " + " ".join(tokens[2:])

        # CTCP PRIVMSGs
        if privmsg_command == '\x01PING':
            self._send_message(Irc.ctcp_pong(sender, message))

        elif privmsg_command[0] == '\x01':
            logger.debug('Missing CTCP command %s', privmsg_command)

    def _handle_identify(self, message):
        if self.config['nick'] != '' and self.config['nick'][0] != '_':
            self._send_message(Irc.identify(self.config['pass']))

    def _handle_notice(self, message):
        # CTCP PONG
        if message.split(" ")[3] == ":\x01PING":
            time_stamp = ".".join(message.split(" ")[-2:])[:-1]
            time_taken = round(time.time() - float(time_stamp[:-1]), 2)
            prefix, command, parameters = Irc.split_message(message)
            user, ident, host = Irc.split_prefix(prefix)

            self.send_event("pong", str(time_taken), user)

    def _set_mode(self, message):
        self._send_message(Irc.mode(self.config['nick'], self.config['mode']))

    def _handle_userlist_update(self, message):
        prefix, command, parameters = Irc.split_message(message)
        split_params = parameters.split(' ')
        users = split_params[3:][:-1]
        # Remove leading ':' from first user.
        users[0] = users[0][1:]
        channel = split_params[2]

        if channel not in self.users:
            self.users[channel] = users
        else:
            self.users[channel].extend(users)

        self.send_event("users", channel, self.users[channel])
        logger.info(" J  | Joined channels: {}".format(self.users))

    def _handle_join(self, message):
        prefix, command, parameters = Irc.split_message(message)
        sender, user, ident = Irc.split_prefix(prefix)

        if sender == self.config['nick']:
            channel = parameters[1:]
            self.channels.append(channel)
            self.users[channel] = []

            self.send_event("join", channel)

    def _handle_part(self, message):
        prefix, command, parameters = Irc.split_message(message)
        sender, user, ident = Irc.split_prefix(prefix)

        if sender == self.config['nick']:
            channel = parameters.split(" ")[0]
            self.users.pop(channel)

            self.send_event("part", channel)

    def _handle_mode(self, message):
        prefix, command, parameters = Irc.split_message(message)

        # Auto-join servers after MODE received from NickServ.
        if prefix.lower() == ':nickserv':
            for channel in self.config['channels']:
                self._send_message(Irc.join(channel))

    def _handle_server_ping(self, message):
        prefix, command, parameters = Irc.split_message(message)

        # PONG any server PINGs with the same parameters.
        self._send_message(Irc.server_pong(parameters))
        self.send_event("server_ping", datetime.datetime.strftime(datetime.datetime.now(), '%H:%M:%S'))

    def _handle_433(self, message):
        prefix, command, parameters = Irc.split_message(message)

        if re.search("Nickname is already in use", parameters):
            self.config['nick'] = "_{}".format(self.config['nick'])
            self._send_message(Irc.nick(self.config['nick']))
            self._send_message(Irc.user(self.config['user'], self.config['unused'], self.config['owner']))
            self._send_message(Irc.mode(self.config['nick'], self.config['mode']))

    # Events
    def _stop_event(self, event):
        self.stop()

    def _send_response_event(self, event):
        event_type, data = event
        self._send_response(*data)

    def _ping_event(self, event):
        event_type, data = event
        message = data[0][0]
        sender = data[0][1]

        try:
            channel = message.split(" ")[2]
            if channel[0] != '#':
                channel = None
        except IndexError:
            channel = None

        try:
            user = message.split(" ")[2]
        except IndexError:
            user = None
            self._send_response("Command: ping <user>", sender, channel)
            return

        unix_timestamp = str(time.time()).replace(".", " ")
        self._send_message(Irc.ctcp_ping(user, unix_timestamp))
        logger.info("Pinging {}".format(user))

    def _join_event(self, event):
        event_type, data = event
        message = data[0][0]
        destination = data[0][1]

        if data[0][2][0] == '#':
            destination = data[0][2]


        channel = message.split(" ")[2]
        if channel[0] == '#':
            self._send_response("Joining {}".format(channel), destination)
            self._send_message(Irc.join(channel))

    def _part_event(self, event):
        event_type, data = event
        message = data[0][0]
        destination = data[0][1]

        if data[0][2][0] == '#':
            destination = data[0][2]

        channel = message.split(" ")[2]
        if channel[0] == '#':
            self._send_response("Parting {}".format(channel), destination)
            self._send_message(Irc.part(channel, "Parting :)"))
