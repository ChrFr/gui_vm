# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'new_project.ui'
#
# Created: Wed Apr 30 16:05:33 2014
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

class Ui_NewProject(object):
    def setupUi(self, NewProject):
        NewProject.setObjectName(_fromUtf8("NewProject"))
        NewProject.resize(409, 159)
        NewProject.setMinimumSize(QtCore.QSize(409, 159))
        NewProject.setMaximumSize(QtCore.QSize(409, 16777215))
        NewProject.setModal(True)
        self.buttonBox = QtGui.QDialogButtonBox(NewProject)
        self.buttonBox.setGeometry(QtCore.QRect(10, 110, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.label = QtGui.QLabel(NewProject)
        self.label.setGeometry(QtCore.QRect(10, 69, 66, 23))
        self.label.setObjectName(_fromUtf8("label"))
        self.folder_browse_button = QtGui.QPushButton(NewProject)
        self.folder_browse_button.setGeometry(QtCore.QRect(357, 69, 30, 23))
        self.folder_browse_button.setMaximumSize(QtCore.QSize(30, 16777215))
        self.folder_browse_button.setObjectName(_fromUtf8("folder_browse_button"))
        self.folder_edit = QtGui.QLineEdit(NewProject)
        self.folder_edit.setGeometry(QtCore.QRect(90, 70, 261, 20))
        self.folder_edit.setObjectName(_fromUtf8("folder_edit"))
        self.project_edit = QtGui.QLineEdit(NewProject)
        self.project_edit.setGeometry(QtCore.QRect(90, 30, 261, 20))
        self.project_edit.setObjectName(_fromUtf8("project_edit"))
        self.label_2 = QtGui.QLabel(NewProject)
        self.label_2.setGeometry(QtCore.QRect(10, 30, 66, 23))
        self.label_2.setObjectName(_fromUtf8("label_2"))

        self.retranslateUi(NewProject)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), NewProject.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), NewProject.reject)
        QtCore.QMetaObject.connectSlotsByName(NewProject)

    def retranslateUi(self, NewProject):
        NewProject.setWindowTitle(_translate("NewProject", "Neues Projekt", None))
        self.label.setText(_translate("NewProject", "Projektordner", None))
        self.folder_browse_button.setText(_translate("NewProject", "...", None))
        self.project_edit.setText(_translate("NewProject", "Neues Projekt", None))
        self.label_2.setText(_translate("NewProject", "Projektname", None))

