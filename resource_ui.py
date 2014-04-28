# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'resource.ui'
#
# Created: Mon Apr 28 17:34:11 2014
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

class Ui_DetailsResource(object):
    def setupUi(self, DetailsResource):
        DetailsResource.setObjectName(_fromUtf8("DetailsResource"))
        DetailsResource.resize(770, 707)
        self.verticalLayout_2 = QtGui.QVBoxLayout(DetailsResource)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_2 = QtGui.QLabel(DetailsResource)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.label = QtGui.QLabel(DetailsResource)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.file_edit = QtGui.QLineEdit(DetailsResource)
        self.file_edit.setReadOnly(True)
        self.file_edit.setObjectName(_fromUtf8("file_edit"))
        self.gridLayout.addWidget(self.file_edit, 1, 2, 1, 1)
        self.browse_button = QtGui.QPushButton(DetailsResource)
        self.browse_button.setMaximumSize(QtCore.QSize(30, 30))
        self.browse_button.setObjectName(_fromUtf8("browse_button"))
        self.gridLayout.addWidget(self.browse_button, 1, 3, 1, 1)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.status_button = QtGui.QPushButton(DetailsResource)
        self.status_button.setObjectName(_fromUtf8("status_button"))
        self.horizontalLayout_2.addWidget(self.status_button)
        self.gridLayout.addLayout(self.horizontalLayout_2, 6, 2, 1, 1)
        self.listWidget = QtGui.QListWidget(DetailsResource)
        self.listWidget.setObjectName(_fromUtf8("listWidget"))
        self.gridLayout.addWidget(self.listWidget, 4, 2, 1, 1)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label_3 = QtGui.QLabel(DetailsResource)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.verticalLayout.addWidget(self.label_3)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.gridLayout.addLayout(self.verticalLayout, 4, 0, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(20, 30, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.gridLayout.addItem(spacerItem2, 2, 2, 1, 1)
        self.project_copy = QtGui.QLabel(DetailsResource)
        self.project_copy.setText(_fromUtf8(""))
        self.project_copy.setObjectName(_fromUtf8("project_copy"))
        self.gridLayout.addWidget(self.project_copy, 0, 2, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout)

        self.retranslateUi(DetailsResource)
        QtCore.QMetaObject.connectSlotsByName(DetailsResource)

    def retranslateUi(self, DetailsResource):
        DetailsResource.setWindowTitle(_translate("DetailsResource", "GroupBox", None))
        DetailsResource.setTitle(_translate("DetailsResource", "GroupBox", None))
        self.label_2.setText(_translate("DetailsResource", "Projektdatei", None))
        self.label.setText(_translate("DetailsResource", "Quelle", None))
        self.browse_button.setText(_translate("DetailsResource", "...", None))
        self.status_button.setText(_translate("DetailsResource", "Status prüfen", None))
        self.label_3.setText(_translate("DetailsResource", "Details", None))

