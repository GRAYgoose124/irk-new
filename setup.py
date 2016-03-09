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
    'description': '\'smart\' irc bot',
    'author': 'Grayson Miller',
    'url': 'URL to get it at.',
    'download_url': 'none',
    'author_email': 'grayson.miller124@gmail.com',
    'version': '0.1',
    'install_requires': ['nose'],
    'packages': ['irk'],
    'entry_points': {
        'console_scripts': [
            'irk = irk.__main__:main'
        ]
    }
}

setup(**config)
