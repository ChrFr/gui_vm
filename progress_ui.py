# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'progress.ui'
#
# Created: Thu May 15 19:19:04 2014
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

class Ui_ProgressDialog(object):
    def setupUi(self, ProgressDialog):
        ProgressDialog.setObjectName(_fromUtf8("ProgressDialog"))
        ProgressDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        ProgressDialog.resize(410, 210)
        ProgressDialog.setMinimumSize(QtCore.QSize(410, 210))
        ProgressDialog.setMaximumSize(QtCore.QSize(410, 10000))
        self.progress_bar = QtGui.QProgressBar(ProgressDialog)
        self.progress_bar.setGeometry(QtCore.QRect(29, 130, 381, 21))
        self.progress_bar.setProperty("value", 24)
        self.progress_bar.setObjectName(_fromUtf8("progress_bar"))
        self.buttonBox = QtGui.QDialogButtonBox(ProgressDialog)
        self.buttonBox.setGeometry(QtCore.QRect(220, 170, 156, 23))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.log_edit = QtGui.QTextEdit(ProgressDialog)
        self.log_edit.setGeometry(QtCore.QRect(30, 20, 345, 101))
        self.log_edit.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.log_edit.setLineWrapMode(QtGui.QTextEdit.NoWrap)
        self.log_edit.setReadOnly(True)
        self.log_edit.setObjectName(_fromUtf8("log_edit"))

        self.retranslateUi(ProgressDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ProgressDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ProgressDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ProgressDialog)

    def retranslateUi(self, ProgressDialog):
        ProgressDialog.setWindowTitle(_translate("ProgressDialog", "Fortschritt", None))

