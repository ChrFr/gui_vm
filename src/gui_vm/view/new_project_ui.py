# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'new_project.ui'
#
# Created: Tue Feb 23 14:02:25 2016
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

class Ui_NewProject(object):
    def setupUi(self, NewProject):
        NewProject.setObjectName(_fromUtf8("NewProject"))
        NewProject.resize(409, 159)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(NewProject.sizePolicy().hasHeightForWidth())
        NewProject.setSizePolicy(sizePolicy)
        NewProject.setMinimumSize(QtCore.QSize(409, 159))
        NewProject.setMaximumSize(QtCore.QSize(409, 159))
        NewProject.setSizeGripEnabled(False)
        NewProject.setModal(True)
        self.gridLayout = QtGui.QGridLayout(NewProject)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(NewProject)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 2, 0, 1, 1)
        self.project_edit = QtGui.QLineEdit(NewProject)
        self.project_edit.setObjectName(_fromUtf8("project_edit"))
        self.gridLayout.addWidget(self.project_edit, 1, 1, 1, 1)
        self.folder_edit = QtGui.QLineEdit(NewProject)
        self.folder_edit.setObjectName(_fromUtf8("folder_edit"))
        self.gridLayout.addWidget(self.folder_edit, 2, 1, 1, 1)
        self.label_2 = QtGui.QLabel(NewProject)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.folder_browse_button = QtGui.QPushButton(NewProject)
        self.folder_browse_button.setMaximumSize(QtCore.QSize(30, 16777215))
        self.folder_browse_button.setObjectName(_fromUtf8("folder_browse_button"))
        self.gridLayout.addWidget(self.folder_browse_button, 2, 2, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(NewProject)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 4, 0, 1, 2)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 0, 1, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 3, 1, 1, 1)

        self.retranslateUi(NewProject)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), NewProject.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), NewProject.reject)
        QtCore.QMetaObject.connectSlotsByName(NewProject)

    def retranslateUi(self, NewProject):
        NewProject.setWindowTitle(_translate("NewProject", "Neues Projekt", None))
        self.label.setText(_translate("NewProject", "Projektordner", None))
        self.project_edit.setText(_translate("NewProject", "Neues Projekt", None))
        self.label_2.setText(_translate("NewProject", "Projektname", None))
        self.folder_browse_button.setText(_translate("NewProject", "...", None))

