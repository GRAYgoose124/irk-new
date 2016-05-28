# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'irk_window.ui'
#
# Created: Sat May 28 02:22:29 2016
#      by: PyQt5 UI code generator 5.3.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(906, 693)
        self.centralWidget = QtWidgets.QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.ChatArea = QtWidgets.QTextEdit(self.centralWidget)
        self.ChatArea.setGeometry(QtCore.QRect(10, 10, 790, 550))
        self.ChatArea.setReadOnly(True)
        self.ChatArea.setObjectName("ChatArea")
        self.StartButton = QtWidgets.QPushButton(self.centralWidget)
        self.StartButton.setGeometry(QtCore.QRect(810, 90, 85, 27))
        self.StartButton.setObjectName("StartButton")
        self.StopButton = QtWidgets.QPushButton(self.centralWidget)
        self.StopButton.setGeometry(QtCore.QRect(810, 120, 85, 27))
        self.StopButton.setObjectName("StopButton")
        self.QuitButton = QtWidgets.QPushButton(self.centralWidget)
        self.QuitButton.setGeometry(QtCore.QRect(810, 10, 85, 27))
        self.QuitButton.setObjectName("QuitButton")
        self.inputArea = QtWidgets.QTextEdit(self.centralWidget)
        self.inputArea.setGeometry(QtCore.QRect(10, 590, 790, 20))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.inputArea.sizePolicy().hasHeightForWidth())
        self.inputArea.setSizePolicy(sizePolicy)
        self.inputArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.inputArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.inputArea.setObjectName("inputArea")
        MainWindow.setCentralWidget(self.centralWidget)
        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 900, 25))
        self.menuBar.setObjectName("menuBar")
        MainWindow.setMenuBar(self.menuBar)
        self.mainToolBar = QtWidgets.QToolBar(MainWindow)
        self.mainToolBar.setObjectName("mainToolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.mainToolBar)
        self.statusBar = QtWidgets.QStatusBar(MainWindow)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.StartButton.setText(_translate("MainWindow", "Start"))
        self.StopButton.setText(_translate("MainWindow", "Stop"))
        self.QuitButton.setText(_translate("MainWindow", "Quit"))
