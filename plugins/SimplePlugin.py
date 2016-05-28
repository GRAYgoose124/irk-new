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
# data['command']
# data['arguments]


# TODO: Document API, use this plugin as API example.
class SimplePlugin:
    def __init__(self):
        return

    # TODO: Make a base plugin class to derive from?
    def privmsg_hook(self, handler, data):
        if data['command'] != 'echo':
            return

        if data['arguments'][0][0] == '#':
            response = " ".join(data['arguments'][1:])
            channel = data['arguments'][0]
            handler.send_response(response, data['sender'], channel)
        else:
            response = " ".join(data['arguments'])
            handler.send_response(response, data['sender'], data['orig_dest'])
