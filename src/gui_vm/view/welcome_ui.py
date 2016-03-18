# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'welcome.ui'
#
# Created: Fri Mar 18 16:05:08 2016
#      by: PyQt4 UI code generator 4.11.2
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

class Ui_Welcome(object):
    def setupUi(self, Welcome):
        Welcome.setObjectName(_fromUtf8("Welcome"))
        Welcome.setEnabled(True)
        Welcome.resize(300, 117)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Welcome.sizePolicy().hasHeightForWidth())
        Welcome.setSizePolicy(sizePolicy)
        Welcome.setMinimumSize(QtCore.QSize(300, 117))
        Welcome.setMaximumSize(QtCore.QSize(300, 139))
        Welcome.setSizeGripEnabled(False)
        Welcome.setModal(True)
        self.gridLayout_2 = QtGui.QGridLayout(Welcome)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.open_button = QtGui.QPushButton(Welcome)
        self.open_button.setMinimumSize(QtCore.QSize(0, 0))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/buttons/icons/open.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.open_button.setIcon(icon)
        self.open_button.setObjectName(_fromUtf8("open_button"))
        self.gridLayout_2.addWidget(self.open_button, 2, 1, 1, 1)
        self.new_button = QtGui.QPushButton(Welcome)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/buttons/icons/plus.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.new_button.setIcon(icon1)
        self.new_button.setObjectName(_fromUtf8("new_button"))
        self.gridLayout_2.addWidget(self.new_button, 2, 0, 1, 1)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.cancel_button = QtGui.QPushButton(Welcome)
        self.cancel_button.setObjectName(_fromUtf8("cancel_button"))
        self.horizontalLayout_2.addWidget(self.cancel_button)
        self.exit_button = QtGui.QPushButton(Welcome)
        self.exit_button.setObjectName(_fromUtf8("exit_button"))
        self.horizontalLayout_2.addWidget(self.exit_button)
        self.gridLayout_2.addLayout(self.horizontalLayout_2, 4, 0, 1, 2)
        spacerItem1 = QtGui.QSpacerItem(20, 35, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.gridLayout_2.addItem(spacerItem1, 3, 1, 1, 1)
        self.label = QtGui.QLabel(Welcome)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 2)
        spacerItem2 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem2, 1, 1, 1, 1)

        self.retranslateUi(Welcome)
        QtCore.QMetaObject.connectSlotsByName(Welcome)

    def retranslateUi(self, Welcome):
        Welcome.setWindowTitle(_translate("Welcome", "Willkommen", None))
        self.open_button.setText(_translate("Welcome", "Projekt öffnen", None))
        self.new_button.setText(_translate("Welcome", "Neues Projekt", None))
        self.cancel_button.setText(_translate("Welcome", "Abbrechen", None))
        self.exit_button.setText(_translate("Welcome", "Beenden", None))
        self.label.setText(_translate("Welcome", "Bitte wählen Sie eine Aktion aus:", None))

import gui_rc
