import argparse
import os
import datetime

# This must be the first statement before other statements.
# You may only put a quoted or triple quoted string,
# Python comments or blank lines before the __future__ line.


def log(message, file=None, t='SIMPLE', silent=False):
    if t == 'SIMPLE':
        message = "   | {0}".format(message)
    elif t == 'SEND':
        message = "<--| {0}".format(message)
    elif t == 'RECEIVE':
        message = "-->| {0}".format(message)
    elif t == 'ERROR':
        message = " X | {0}".format(message)
    elif t == 'SYSINFO':
        message = " ! | {0}".format(message)
    elif t == 'INFO':
        message = " O | {0}".format(message)

    if not silent:
        print message

    if file is not None:
	file.write("{0}\n".format(message))


def cwdopen(filename, mode='r'):
    """Check whether to prepend the CWD or not based on the filename."""
    print " ! | Opened file {0} with {1} permissions.".format(filename, mode)

    try:
        if os.path.isabs(filename):
            return open(filename, mode)
        else:
            return open(os.path.join(os.getcwd(), filename), mode)
    except IOError as e:
        print("EXC| Error: file not found.")
        return None


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', type=str, help="Configuration file. defaults to: \'~/.irk\'")
    #parser.add_argument(''
    #args = parser.parse_args()
    return args

def timestamp():
    return int((datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds() * 1000)
