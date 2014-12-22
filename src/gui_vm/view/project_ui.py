# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'project.ui'
#
# Created: Mon Dec 22 17:20:23 2014
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

class Ui_DetailsProject(object):
    def setupUi(self, DetailsProject):
        DetailsProject.setObjectName(_fromUtf8("DetailsProject"))
        DetailsProject.resize(400, 406)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(DetailsProject.sizePolicy().hasHeightForWidth())
        DetailsProject.setSizePolicy(sizePolicy)
        DetailsProject.setMinimumSize(QtCore.QSize(400, 0))
        self.gridLayoutWidget = QtGui.QWidget(DetailsProject)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(10, 20, 371, 331))
        self.gridLayoutWidget.setObjectName(_fromUtf8("gridLayoutWidget"))
        self.gridLayout = QtGui.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setMargin(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.folder_edit = QtGui.QLineEdit(self.gridLayoutWidget)
        self.folder_edit.setReadOnly(True)
        self.folder_edit.setObjectName(_fromUtf8("folder_edit"))
        self.gridLayout.addWidget(self.folder_edit, 0, 1, 1, 1)
        self.label = QtGui.QLabel(self.gridLayoutWidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.meta_layout = QtGui.QFormLayout()
        self.meta_layout.setObjectName(_fromUtf8("meta_layout"))
        self.gridLayout.addLayout(self.meta_layout, 1, 0, 1, 3)

        self.retranslateUi(DetailsProject)
        QtCore.QMetaObject.connectSlotsByName(DetailsProject)

    def retranslateUi(self, DetailsProject):
        DetailsProject.setWindowTitle(_translate("DetailsProject", "GroupBox", None))
        DetailsProject.setTitle(_translate("DetailsProject", "GroupBox", None))
        self.label.setText(_translate("DetailsProject", "Projektordner", None))

