# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'progress.ui'
#
# Created: Tue Oct 28 17:45:36 2014
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

class Ui_ProgressDialog(object):
    def setupUi(self, ProgressDialog):
        ProgressDialog.setObjectName(_fromUtf8("ProgressDialog"))
        ProgressDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        ProgressDialog.resize(410, 210)
        ProgressDialog.setMinimumSize(QtCore.QSize(410, 210))
        ProgressDialog.setMaximumSize(QtCore.QSize(410, 10000))
        self.progress_bar = QtGui.QProgressBar(ProgressDialog)
        self.progress_bar.setGeometry(QtCore.QRect(29, 130, 381, 21))
        self.progress_bar.setProperty("value", 0)
        self.progress_bar.setObjectName(_fromUtf8("progress_bar"))
        self.log_edit = QtGui.QTextEdit(ProgressDialog)
        self.log_edit.setGeometry(QtCore.QRect(30, 20, 345, 101))
        self.log_edit.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.log_edit.setLineWrapMode(QtGui.QTextEdit.NoWrap)
        self.log_edit.setReadOnly(True)
        self.log_edit.setObjectName(_fromUtf8("log_edit"))
        self.horizontalLayoutWidget = QtGui.QWidget(ProgressDialog)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(190, 160, 181, 31))
        self.horizontalLayoutWidget.setObjectName(_fromUtf8("horizontalLayoutWidget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.startButton = QtGui.QPushButton(self.horizontalLayoutWidget)
        self.startButton.setObjectName(_fromUtf8("startButton"))
        self.horizontalLayout.addWidget(self.startButton)
        self.cancelButton = QtGui.QPushButton(self.horizontalLayoutWidget)
        self.cancelButton.setObjectName(_fromUtf8("cancelButton"))
        self.horizontalLayout.addWidget(self.cancelButton)

        self.retranslateUi(ProgressDialog)
        QtCore.QMetaObject.connectSlotsByName(ProgressDialog)

    def retranslateUi(self, ProgressDialog):
        ProgressDialog.setWindowTitle(_translate("ProgressDialog", "Fortschritt", None))
        self.startButton.setText(_translate("ProgressDialog", "Start", None))
        self.cancelButton.setText(_translate("ProgressDialog", "Abbrechen", None))

