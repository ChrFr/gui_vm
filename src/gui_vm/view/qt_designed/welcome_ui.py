# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'welcome.ui'
#
# Created: Tue Nov 18 18:14:31 2014
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
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Welcome.sizePolicy().hasHeightForWidth())
        Welcome.setSizePolicy(sizePolicy)
        Welcome.setMinimumSize(QtCore.QSize(300, 117))
        Welcome.setMaximumSize(QtCore.QSize(409, 159))
        Welcome.setSizeGripEnabled(False)
        Welcome.setModal(True)
        self.verticalLayoutWidget = QtGui.QWidget(Welcome)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(0, 10, 301, 101))
        self.verticalLayoutWidget.setObjectName(_fromUtf8("verticalLayoutWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.new_button = QtGui.QPushButton(self.verticalLayoutWidget)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/buttons/icons/plus.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.new_button.setIcon(icon)
        self.new_button.setObjectName(_fromUtf8("new_button"))
        self.gridLayout.addWidget(self.new_button, 0, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 0, 1, 1)
        self.open_button = QtGui.QPushButton(self.verticalLayoutWidget)
        self.open_button.setMinimumSize(QtCore.QSize(0, 0))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/buttons/icons/open.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.open_button.setIcon(icon1)
        self.open_button.setObjectName(_fromUtf8("open_button"))
        self.gridLayout.addWidget(self.open_button, 0, 2, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 0, 3, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem2)
        self.cancel_button = QtGui.QPushButton(self.verticalLayoutWidget)
        self.cancel_button.setObjectName(_fromUtf8("cancel_button"))
        self.horizontalLayout_2.addWidget(self.cancel_button)
        self.exit_button = QtGui.QPushButton(self.verticalLayoutWidget)
        self.exit_button.setObjectName(_fromUtf8("exit_button"))
        self.horizontalLayout_2.addWidget(self.exit_button)
        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(Welcome)
        QtCore.QMetaObject.connectSlotsByName(Welcome)

    def retranslateUi(self, Welcome):
        Welcome.setWindowTitle(_translate("Welcome", "Willkommen", None))
        self.new_button.setText(_translate("Welcome", "Neues Projekt", None))
        self.open_button.setText(_translate("Welcome", "Projekt öffnen", None))
        self.cancel_button.setText(_translate("Welcome", "Abbrechen", None))
        self.exit_button.setText(_translate("Welcome", "Beenden", None))

import gui_rc
