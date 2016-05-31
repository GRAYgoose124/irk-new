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
# data['original_destination']
# data['message']


# TODO: Document API, use this plugin as API example.
class SimplePlugin:
    def __init__(self, handler):
        self.handler = handler
        self.handler.command_dict['sample_command'] = self.sample_command

    # TODO: echo test
    def sample_command(self, data):
        print("Command World!")

    # TODO: Expose ui to plugins.
    def privmsg_hook(self, data):
        pass
        # print("Hello World!")

        # response = "Hello World!"
        # channel = "#testgrounds"
        # self.handler.send_response(response, data['sender'], channel)
