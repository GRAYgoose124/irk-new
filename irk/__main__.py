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

import irctools
import irc
import bot

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
    logging.basicConfig(level=logging.DEBUG)
    root = logging.getLogger()
    root.addHandler(logging.FileHandler(os.path.join(home_dir, "logs/irk.log"), 'w'))

    client = bot.IrcBot(home_dir, config)

    # Make non-blocking
    try:
        client.start()
    except KeyboardInterrupt:
        client.stop()
        
