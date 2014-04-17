# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_window.ui'
#
# Created: Thu Apr 17 08:52:09 2014
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(714, 650)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setSizeConstraint(QtGui.QLayout.SetMaximumSize)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.project_tree_view = QtGui.QTreeView(self.centralwidget)
        self.project_tree_view.setObjectName(_fromUtf8("project_tree_view"))
        self.verticalLayout_2.addWidget(self.project_tree_view)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.minus_button = QtGui.QToolButton(self.centralwidget)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/buttons/icons/minus.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.minus_button.setIcon(icon)
        self.minus_button.setObjectName(_fromUtf8("minus_button"))
        self.horizontalLayout_2.addWidget(self.minus_button)
        self.plus_button = QtGui.QToolButton(self.centralwidget)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/buttons/icons/plus.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.plus_button.setIcon(icon1)
        self.plus_button.setIconSize(QtCore.QSize(16, 16))
        self.plus_button.setObjectName(_fromUtf8("plus_button"))
        self.horizontalLayout_2.addWidget(self.plus_button)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3.addLayout(self.verticalLayout_2)
        self.verticalLayout_4 = QtGui.QVBoxLayout()
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.detail_text_output = QtGui.QTextEdit(self.centralwidget)
        self.detail_text_output.setReadOnly(True)
        self.detail_text_output.setObjectName(_fromUtf8("detail_text_output"))
        self.verticalLayout_4.addWidget(self.detail_text_output)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.verticalLayout_4.addItem(spacerItem)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem1)
        self.start_button = QtGui.QPushButton(self.centralwidget)
        self.start_button.setObjectName(_fromUtf8("start_button"))
        self.horizontalLayout_4.addWidget(self.start_button)
        self.verticalLayout_4.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_3.addLayout(self.verticalLayout_4)
        self.gridLayout.addLayout(self.horizontalLayout_3, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 714, 21))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuDatei = QtGui.QMenu(self.menubar)
        self.menuDatei.setObjectName(_fromUtf8("menuDatei"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.actionBeenden = QtGui.QAction(MainWindow)
        self.actionBeenden.setObjectName(_fromUtf8("actionBeenden"))
        self.actionProjekt_ffnen = QtGui.QAction(MainWindow)
        self.actionProjekt_ffnen.setObjectName(_fromUtf8("actionProjekt_ffnen"))
        self.actionProjekt_speichern = QtGui.QAction(MainWindow)
        self.actionProjekt_speichern.setObjectName(_fromUtf8("actionProjekt_speichern"))
        self.menuDatei.addAction(self.actionProjekt_ffnen)
        self.menuDatei.addAction(self.actionProjekt_speichern)
        self.menuDatei.addAction(self.actionBeenden)
        self.menubar.addAction(self.menuDatei.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.minus_button.setText(_translate("MainWindow", "...", None))
        self.plus_button.setText(_translate("MainWindow", "...", None))
        self.start_button.setText(_translate("MainWindow", "Simulation starten", None))
        self.menuDatei.setTitle(_translate("MainWindow", "Datei", None))
        self.actionBeenden.setText(_translate("MainWindow", "Beenden", None))
        self.actionProjekt_ffnen.setText(_translate("MainWindow", "Projekt öffnen", None))
        self.actionProjekt_speichern.setText(_translate("MainWindow", "Projekt speichern", None))

import gui_rc
