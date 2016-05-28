#   Irk: irc bot
#   Copyright (C) 2016  Grayson Miller

#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.

#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.

#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>
import logging
import sys

from PyQt5.QtCore import *
from PyQt5.QtWidgets import  *

from irk.bot import IrcBot
from irk.irk_window import Ui_MainWindow

logging.basicConfig(level=logging.DEBUG, format='[%(levelname)7s] %(name)8s:%(lineno)3s | %(message)s')
logger = logging.getLogger(__name__)

class IrkMainThread(QThread):
    def __init__(self, ui):
        self.ui = ui
        self.client = None
        QThread.__init__(self)

    def run(self):
        home_directory = ".irk"
        self.client = IrcBot(home_directory)
        self.client.chat_update.connect(self.ui.ChatArea.append)
        self.client.start()

    def terminate(self):
        if self.client is not None:
            self.client.stop()
            self.client = None
        QThread.terminate(self)



class IrkWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        ui = Ui_MainWindow()
        self.irk_thread = IrkMainThread(ui)

        ui.setupUi(self)
        ui.StartButton.clicked.connect(self.irk_thread.start)
        ui.StopButton.clicked.connect(self.irk_thread.terminate)
        ui.QuitButton.clicked.connect(self.quit)

        # TODO: Connect UI input and feed to bot.

        self.setWindowTitle('Irk')
        self.show()

    def quit(self):
        if self.irk_thread.client is not None:
            self.irk_thread.client.stop()
        QCoreApplication.instance().quit()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    window = IrkWindow()

    sys.exit(app.exec())
