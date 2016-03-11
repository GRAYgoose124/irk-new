class SimplePlugin:
    def command_hook(self, handler, data):
        sender_nick, hostname, destination, command, params = data

        message = "+ +".join(params)

        if command == '!test':
            if destination[0] == "#":
                handler.privmsg(destination, message)
            elif destination == handler.config['nick']:
                handler.privmsg(sender_nick, message)
