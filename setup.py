#!/usr/bin/env python
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
from setuptools import setup

config = {
    'name': 'irk',
    'description': 'A \'smart\' irc bot with plugins.',
    'author': 'Grayson Miller',
    'url': 'https://github.com/GRAYgoose124/irk',
    'download_url': 'git@github.com:GRAYgoose124/irk.git',
    'author_email': 'grayson.miller124@gmail.com',
    'version': '0.0.4',
    'packages': ['irk'],
    'entry_points': {
        'console_scripts': [
            'irk = irk.__main__:main'
        ]
    }
}

setup(**config)
