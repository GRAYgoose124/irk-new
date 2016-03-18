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

#
# data['sender']
# data['ident']
# data['orig_dest']
# data['command'] #TODO: combine command+arguments
# data['arguments]


# TODO: Document API, use this plugin as API example.
# TODO: Turn into entire package plugin system
class SimplePlugin:
    def __init__(self):
        return

    def privmsg_hook(self, handler, data):
        if data['command'] != 'echo':
            return

        response = " ".join(data['arguments'])

        # TODO: Add to API helper functions?

        handler.send_response(response, data['sender'], data['orig_dest'])