import os
import json

from utils import cwdopen, pretty

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
