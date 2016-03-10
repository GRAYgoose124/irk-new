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
import os
import logging
import sys

import irctools
from ircbot import IrcBot


# TODO: Load plugins (in bot class) (live reload) (permissions, etc)


# TODO: Logging from command line, regen config, etc.
def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', type=str,
                        help="Configuration file. defaults to: \'~/.irk\'")
    #parser.add_argument(''
    #args = parser.parse_args()
    return args

            
def main():
    home_dir, subfolders = irctools.init_homedir(".irk")
    
    config_filename = os.path.join(home_dir, "config")
    config = irctools.init_or_load_config(config_filename)

    # Log to file
    logging.addLevelName(25, "OUT")
    logging.basicConfig(level=25)
    root = logging.getLogger()
    shandler = logging.StreamHandler(sys.stdout)
    fhandler = logging.FileHandler(os.path.join(home_dir,
                                                "logs/irk.log"), 'w')

    simple_format = logging.Formatter('[%(levelname)7s]%(message)s')
    complex_format = logging.Formatter('[%(levelname)7s:%(name)15s] |%(message)s')
    shandler.setFormatter(simple_format)
    fhandler.setFormatter(complex_format)
    root.addHandler(fhandler)
    root.addHandler(shandler)

    client = IrcBot(home_dir, config)

    # Make non-blocking
    try:
        client.start()
    except KeyboardInterrupt:
        client.stop()
        
