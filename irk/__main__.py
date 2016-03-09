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
import irc
import os
import json
import logging
import sys

from utils import cwdopen, pretty, timestamp
import irchelpers

# TODO: Load plugins (in bot class) (live reload) (permissions, etc)

def init_homedir(directory):
    if os.path.isabs(directory):
        root = ''
    else:
        root = os.path.expanduser("~")

    homedir = os.path.join(root, directory)
    folders = ["plugins", "logs"]

    if not os.path.exists(homedir):
        os.makedirs(homedir)

    for i, folder in enumerate(folders):
        folders[i] = os.path.join(homedir, folder)
        if not os.path.exists(folders[i]):
            os.mkdir(folders[i])

    return homedir, folders


# TODO: Logging from command line, regen config, etc.
def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', type=str,
                        help="Configuration file. defaults to: \'~/.irk\'")
    #parser.add_argument(''
    #args = parser.parse_args()
    return args

            
def main():
    home_dir, subfolders = init_homedir(".irk")
    
    config_filename = os.path.join(home_dir, "config")
    config = irchelpers.init_or_load_config(config_filename)

    # Log to file 
    logging.basicConfig(level=logging.DEBUG)
    root = logging.getLogger()
    root.addHandler(logging.FileHandler(os.path.join(home_dir, "logs/irk.log"), 'w'))

    client = irc.IrcClient(home_dir, config)

    # Make non-blocking
    try:
        client.start()
    except KeyboardInterrupt:
        client.stop()
        
