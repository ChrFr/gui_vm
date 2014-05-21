# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'welcome.ui'
#
# Created: Wed May 21 18:05:58 2014
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

class Ui_Welcome(object):
    def setupUi(self, Welcome):
        Welcome.setObjectName(_fromUtf8("Welcome"))
        Welcome.resize(409, 159)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Welcome.sizePolicy().hasHeightForWidth())
        Welcome.setSizePolicy(sizePolicy)
        Welcome.setMinimumSize(QtCore.QSize(409, 159))
        Welcome.setMaximumSize(QtCore.QSize(409, 159))
        Welcome.setSizeGripEnabled(False)
        Welcome.setModal(True)
        self.verticalLayoutWidget = QtGui.QWidget(Welcome)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 20, 391, 151))
        self.verticalLayoutWidget.setObjectName(_fromUtf8("verticalLayoutWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.new_button = QtGui.QPushButton(self.verticalLayoutWidget)
        self.new_button.setObjectName(_fromUtf8("new_button"))
        self.horizontalLayout.addWidget(self.new_button)
        self.open_button = QtGui.QPushButton(self.verticalLayoutWidget)
        self.open_button.setMinimumSize(QtCore.QSize(0, 0))
        self.open_button.setObjectName(_fromUtf8("open_button"))
        self.horizontalLayout.addWidget(self.open_button)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
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

