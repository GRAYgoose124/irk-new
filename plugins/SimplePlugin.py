# TODO: Document API, use this plugin as API example.

class SimplePlugin:
    def privmsg_hook(self, handler, data):
        if data['command'] != '!test':
            return

        response = ""

        if data['orig_dest'][0] == "#":
            handler.privmsg(data['orig_dest'], response)
        elif data['orig_dest'] == handler.config['nick']:
            handler.privmsg(data['sender'], response)