# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_window.ui'
#
# Created: Wed Apr 30 13:42:06 2014
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
        MainWindow.resize(1040, 711)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.start_button = QtGui.QPushButton(self.centralwidget)
        self.start_button.setMaximumSize(QtCore.QSize(100, 16777215))
        self.start_button.setObjectName(_fromUtf8("start_button"))
        self.horizontalLayout_2.addWidget(self.start_button)
        self.gridLayout.addLayout(self.horizontalLayout_2, 6, 1, 1, 1)
        self.gridLayout_4 = QtGui.QGridLayout()
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.label_3 = QtGui.QLabel(self.centralwidget)
        self.label_3.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout_4.addWidget(self.label_3, 1, 7, 1, 1)
        self.minus_button = QtGui.QToolButton(self.centralwidget)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/buttons/icons/minus.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.minus_button.setIcon(icon)
        self.minus_button.setObjectName(_fromUtf8("minus_button"))
        self.gridLayout_4.addWidget(self.minus_button, 1, 2, 1, 1)
        self.plus_button = QtGui.QToolButton(self.centralwidget)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/buttons/icons/plus.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.plus_button.setIcon(icon1)
        self.plus_button.setIconSize(QtCore.QSize(16, 16))
        self.plus_button.setObjectName(_fromUtf8("plus_button"))
        self.gridLayout_4.addWidget(self.plus_button, 1, 0, 1, 1)
        self.label = QtGui.QLabel(self.centralwidget)
        self.label.setMaximumSize(QtCore.QSize(50, 16777215))
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_4.addWidget(self.label, 1, 1, 1, 1)
        self.save_button = QtGui.QPushButton(self.centralwidget)
        self.save_button.setMaximumSize(QtCore.QSize(35, 35))
        self.save_button.setText(_fromUtf8(""))
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/buttons/icons/save.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.save_button.setIcon(icon2)
        self.save_button.setIconSize(QtCore.QSize(22, 22))
        self.save_button.setObjectName(_fromUtf8("save_button"))
        self.gridLayout_4.addWidget(self.save_button, 1, 6, 1, 1)
        self.label_2 = QtGui.QLabel(self.centralwidget)
        self.label_2.setMaximumSize(QtCore.QSize(50, 16777215))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_4.addWidget(self.label_2, 1, 3, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_4, 3, 0, 1, 1)
        self.project_tree_view = QtGui.QTreeView(self.centralwidget)
        self.project_tree_view.setMaximumSize(QtCore.QSize(500, 16777215))
        self.project_tree_view.setObjectName(_fromUtf8("project_tree_view"))
        self.gridLayout.addWidget(self.project_tree_view, 5, 0, 1, 1)
        self.details_layout = QtGui.QVBoxLayout()
        self.details_layout.setObjectName(_fromUtf8("details_layout"))
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.details_layout.addItem(spacerItem1)
        self.gridLayout.addLayout(self.details_layout, 3, 1, 3, 1)
        self.horizontalLayout.addLayout(self.gridLayout)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1040, 21))
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
        self.actionNeues_Projekt = QtGui.QAction(MainWindow)
        self.actionNeues_Projekt.setObjectName(_fromUtf8("actionNeues_Projekt"))
        self.menuDatei.addAction(self.actionNeues_Projekt)
        self.menuDatei.addAction(self.actionProjekt_ffnen)
        self.menuDatei.addAction(self.actionProjekt_speichern)
        self.menuDatei.addSeparator()
        self.menuDatei.addAction(self.actionBeenden)
        self.menubar.addAction(self.menuDatei.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.start_button.setText(_translate("MainWindow", "Simulation starten", None))
        self.label_3.setText(_translate("MainWindow", "Save ", None))
        self.minus_button.setText(_translate("MainWindow", "...", None))
        self.plus_button.setText(_translate("MainWindow", "...", None))
        self.label.setText(_translate("MainWindow", "Add ", None))
        self.label_2.setText(_translate("MainWindow", "Remove ", None))
        self.menuDatei.setTitle(_translate("MainWindow", "Datei", None))
        self.actionBeenden.setText(_translate("MainWindow", "Beenden", None))
        self.actionProjekt_ffnen.setText(_translate("MainWindow", "Projekt öffnen", None))
        self.actionProjekt_speichern.setText(_translate("MainWindow", "Projekt speichern", None))
        self.actionNeues_Projekt.setText(_translate("MainWindow", "Neues Projekt", None))

import gui_rc
