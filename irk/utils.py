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
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>
import argparse
import os
import datetime
import logging

logger = logging.getLogger(__name__)

def pretty(message, t='SIMPLE'):
    m = None
    if t == 'SIMPLE':
        m = "   | {0}"
    elif t == 'SEND':
        m = "<--| {0}"
    elif t == 'RECEIVE':
        m = "-->| {0}"
    elif t == 'INFO':
        m = " O | {0}"
    elif t == 'CLI':
        m = "CLI| {0}"
    elif t == 'SYSINFO':
        m = " ! | {0}"
    return m.format(message)

def cwdopen(filename, mode='r'):
    """Check whether to prepend the CWD or not based on the filename."""
    logger.debug("Opened file {0} with '{1}' permissions.".format(filename, mode))

    try:
        if os.path.isabs(filename):
            return open(filename, mode)
        else:
            return open(os.path.join(os.getcwd(), filename), mode)
    except IOError as e:
        logger.error("File not found.")
        return None

def timestamp():
    return int((datetime.datetime.utcnow()
                - datetime.datetime(1970, 1, 1)).total_seconds() * 1000)
