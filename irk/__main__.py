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
import sys
import logging
from PyQt5 import QtCore, QtWidgets

from irk.irk_window import Ui_MainWindow
from irk.bot import IrcBot
from irk.protocol import IrcProtocol

logging.basicConfig(level=logging.DEBUG, format='[%(levelname)7s] %(name)8s:%(lineno)3s | %(message)s')
logger = logging.getLogger(__name__)


class IrcBotThread(QtCore.QThread):
    def __init__(self, root_directory, config_filename="config"):
        logger.debug("Bot thread initialized.")
        super(IrcBotThread, self).__init__()

        # TODO: Include multi-client support. Command-line switch.
        self.client = IrcBot(root_directory, config_filename)

    def run(self):
        self.client.start()

    def terminate(self):
        self.client.stop()
        super(IrcBotThread, self).terminate()


# noinspection PyArgumentList
class IrkWindow(QtWidgets.QMainWindow):
    def __init__(self, root_directory, parent=None):
        super(IrkWindow, self).__init__(parent)
        self.ui = Ui_MainWindow()

        # TODO: Command line switch for root directory
        self.client_thread = IrcBotThread(root_directory)

        self.ui.setupUi(self)
        self.ui.QuitButton.clicked.connect(self.quit)
        self.ui.StartButton.clicked.connect(self.client_thread.start)
        self.ui.StopButton.clicked.connect(self.stop)

        self.client_thread.client.message_received.connect(self.ui.ChatArea.append)
        self.client_thread.client.message_sent.connect(self.ui.ChatArea.append)

        self.ui.SendButton.clicked.connect(self.process_input)
        self.ui.inputArea.returnPressed.connect(self.ui.SendButton.click)

        self.client_thread.client.channel_joined.connect(self.add_channel_to_list)
        self.client_thread.client.channel_part.connect(self.remove_channel_from_list)

        self.setWindowTitle('Irk')
        self.setWindowFlags(QtCore.Qt.Tool)
        self.show()

    def add_channel_to_list(self, channel):
        new_channel = QtWidgets.QListWidgetItem(channel)
        self.ui.ChannelList.addItem(new_channel)
        self.ui.ChannelList.setCurrentItem(new_channel)

    def remove_channel_from_list(self, channel):
        matches = self.ui.ChannelList.findItems(channel, QtCore.Qt.MatchExactly)
        if matches is not None:
            row = self.ui.ChannelList.row(matches[0])
            if row != 0:
                self.ui.ChannelList.takeItem(row)

    # TODO: Temporary...This is /so/ bad. Change
    def process_input(self):
        if self.client_thread.client is not None:
            if self.client_thread.client.sock is not None:
                message = self.ui.inputArea.text()
                if message[0] == '/':
                    packet = message[1:].split(' ')
                    command = packet[0]

                    # TODO: Fix this. Hacking bot input together...
                    data = {'sender': None,
                            'original_destination': None,
                            'message': message[1:]}

                    if command in self.client_thread.client.command_dict:

                        self.client_thread.client.command_dict[command](data)
                else:
                    self.client_thread.client.send_message(IrcProtocol.privmsg(self.ui.ChannelList.currentItem().text(),
                                                                               message))
            self.ui.inputArea.clear()

    @QtCore.pyqtSlot()
    def quit(self):
        self.client_thread.terminate()
        QtCore.QCoreApplication.instance().quit()

    @QtCore.pyqtSlot()
    def stop(self):
        self.ui.ChannelList.clear()
        self.client_thread.terminate()


def main():
    app = QtWidgets.QApplication(sys.argv)

    root_directory = "/home/goose/.irk"
    window = IrkWindow(root_directory)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

