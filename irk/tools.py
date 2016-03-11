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
import os
import json
import logging
import getpass

from utils import pretty, cwdopen

logger = logging.getLogger(__name__)

# Merge with utils

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


required_irc_config = {
    'host': 'irc.foonetic.net', 'port': 7001, 'ipv6': False,
    'nick': '', 'pass': '',
    'ident': '', 'user': '',
    'mode': '+B', 'unused': '*',
    'owner': '', 'owner_email': '',
    'channels': [],
    'logging': True
 }


def init_or_load_config(config_file):
    config = None
    changed = False
    
    if not os.path.exists(config_file):
        with cwdopen(config_file, 'w') as file:
            json.dump(required_irc_config, file, indent=2)
            
    config = json.load(cwdopen(config_file, 'r'))
    # TODO: Check for interactivity
    for key, value in config.iteritems():
        if value is None or value == '' and key != 'pass':
            config[key] = str(raw_input(pretty("{}: ".format(key), 'CLI')))
            changed = True
        elif key == 'pass' and value == '':
            config[key] = getpass.getpass(pretty("pass: ", 'CLI'))
            changed = True
        elif key == 'channels' and value == []:
            i = None
            print pretty("To finish, enter DONE.", 'CLI')
            while i != "DONE":
                i = str(raw_input(pretty("channel: ", 'CLI')))
                if i[0] == '#':
                    config[key].append(i)
            changed = True

    if changed:
        with cwdopen(config_file, 'w') as file:
            json.dump(config, file, indent=2)

    return config
