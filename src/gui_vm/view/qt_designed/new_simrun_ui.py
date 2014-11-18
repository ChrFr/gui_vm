# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'new_simrun.ui'
#
# Created: Tue Nov 18 18:14:30 2014
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

class Ui_NewSimRun(object):
    def setupUi(self, NewSimRun):
        NewSimRun.setObjectName(_fromUtf8("NewSimRun"))
        NewSimRun.resize(409, 159)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(NewSimRun.sizePolicy().hasHeightForWidth())
        NewSimRun.setSizePolicy(sizePolicy)
        NewSimRun.setMinimumSize(QtCore.QSize(409, 159))
        NewSimRun.setMaximumSize(QtCore.QSize(409, 159))
        NewSimRun.setSizeGripEnabled(False)
        NewSimRun.setModal(True)
        self.gridLayout = QtGui.QGridLayout(NewSimRun)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.name_edit = QtGui.QLineEdit(NewSimRun)
        self.name_edit.setText(_fromUtf8(""))
        self.name_edit.setObjectName(_fromUtf8("name_edit"))
        self.gridLayout.addWidget(self.name_edit, 1, 1, 1, 1)
        self.label_2 = QtGui.QLabel(NewSimRun)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.folder_browse_button = QtGui.QPushButton(NewSimRun)
        self.folder_browse_button.setMaximumSize(QtCore.QSize(30, 16777215))
        self.folder_browse_button.setObjectName(_fromUtf8("folder_browse_button"))
        self.gridLayout.addWidget(self.folder_browse_button, 2, 2, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(NewSimRun)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 6, 0, 1, 2)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 0, 1, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 4, 1, 1, 1)
        self.combo_model = QtGui.QComboBox(NewSimRun)
        self.combo_model.setObjectName(_fromUtf8("combo_model"))
        self.gridLayout.addWidget(self.combo_model, 2, 1, 1, 1)
        self.label_3 = QtGui.QLabel(NewSimRun)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)

        self.retranslateUi(NewSimRun)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), NewSimRun.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), NewSimRun.reject)
        QtCore.QMetaObject.connectSlotsByName(NewSimRun)

    def retranslateUi(self, NewSimRun):
        NewSimRun.setWindowTitle(_translate("NewSimRun", "Neues Szenario", None))
        self.label_2.setText(_translate("NewSimRun", "Szenarioname", None))
        self.folder_browse_button.setText(_translate("NewSimRun", "...", None))
        self.label_3.setText(_translate("NewSimRun", "Verkehrsmodell", None))

