# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


# noinspection PyArgumentList
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(753, 528)
        self.centralWidget = QtWidgets.QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.QuitButton = QtWidgets.QPushButton(self.centralWidget)
        self.QuitButton.setGeometry(QtCore.QRect(660, 40, 80, 22))
        self.QuitButton.setObjectName("QuitButton")
        self.SendButton = QtWidgets.QPushButton(self.centralWidget)
        self.SendButton.setGeometry(QtCore.QRect(480, 440, 80, 22))
        self.SendButton.setObjectName("SendButton")
        self.inputArea = QtWidgets.QLineEdit(self.centralWidget)
        self.inputArea.setGeometry(QtCore.QRect(10, 440, 461, 22))
        self.inputArea.setObjectName("inputArea")
        self.ChatArea = QtWidgets.QTextEdit(self.centralWidget)
        self.ChatArea.setGeometry(QtCore.QRect(10, 10, 551, 421))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ChatArea.sizePolicy().hasHeightForWidth())
        self.ChatArea.setSizePolicy(sizePolicy)
        self.ChatArea.setReadOnly(True)
        self.ChatArea.setObjectName("ChatArea")
        self.layoutWidget = QtWidgets.QWidget(self.centralWidget)
        self.layoutWidget.setGeometry(QtCore.QRect(570, 70, 171, 391))
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName("verticalLayout")
        self.ChannelList = QtWidgets.QListWidget(self.layoutWidget)
        self.ChannelList.setObjectName("ChannelList")
        self.verticalLayout.addWidget(self.ChannelList)
        self.listWidget_2 = QtWidgets.QListWidget(self.layoutWidget)
        self.listWidget_2.setObjectName("listWidget_2")
        self.verticalLayout.addWidget(self.listWidget_2)
        self.StartButton = QtWidgets.QPushButton(self.centralWidget)
        self.StartButton.setGeometry(QtCore.QRect(570, 10, 80, 22))
        self.StartButton.setObjectName("StartButton")
        self.StopButton = QtWidgets.QPushButton(self.centralWidget)
        self.StopButton.setGeometry(QtCore.QRect(570, 40, 80, 22))
        self.StopButton.setObjectName("StopButton")
        MainWindow.setCentralWidget(self.centralWidget)
        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 753, 19))
        self.menuBar.setObjectName("menuBar")
        self.menuIrk = QtWidgets.QMenu(self.menuBar)
        self.menuIrk.setObjectName("menuIrk")
        MainWindow.setMenuBar(self.menuBar)
        self.mainToolBar = QtWidgets.QToolBar(MainWindow)
        self.mainToolBar.setObjectName("mainToolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.mainToolBar)
        self.statusBar = QtWidgets.QStatusBar(MainWindow)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)
        self.actionLoad_Config_File = QtWidgets.QAction(MainWindow)
        self.actionLoad_Config_File.setObjectName("actionLoad_Config_File")
        self.menuBar.addAction(self.menuIrk.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.QuitButton.setText(_translate("MainWindow", "Quit"))
        self.SendButton.setText(_translate("MainWindow", "Send"))
        self.StartButton.setText(_translate("MainWindow", "Start"))
        self.StopButton.setText(_translate("MainWindow", "Stop"))
        self.menuIrk.setTitle(_translate("MainWindow", "File"))
        self.actionLoad_Config_File.setText(_translate("MainWindow", "Load Config File"))

