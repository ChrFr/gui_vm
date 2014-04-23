# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'resource.ui'
#
# Created: Wed Apr 23 14:38:45 2014
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
        DetailsResource.resize(408, 311)
        self.gridLayoutWidget = QtGui.QWidget(DetailsResource)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(10, 20, 391, 281))
        self.gridLayoutWidget.setObjectName(_fromUtf8("gridLayoutWidget"))
        self.gridLayout = QtGui.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setMargin(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(self.gridLayoutWidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.browse_button = QtGui.QPushButton(self.gridLayoutWidget)
        self.browse_button.setMaximumSize(QtCore.QSize(30, 30))
        self.browse_button.setObjectName(_fromUtf8("browse_button"))
        self.gridLayout.addWidget(self.browse_button, 0, 2, 1, 1)
        self.file_edit = QtGui.QLineEdit(self.gridLayoutWidget)
        self.file_edit.setObjectName(_fromUtf8("file_edit"))
        self.gridLayout.addWidget(self.file_edit, 0, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 1, 1, 1, 1)

        self.retranslateUi(DetailsResource)
        QtCore.QMetaObject.connectSlotsByName(DetailsResource)

    def retranslateUi(self, DetailsResource):
        DetailsResource.setWindowTitle(_translate("DetailsResource", "GroupBox", None))
        DetailsResource.setTitle(_translate("DetailsResource", "GroupBox", None))
        self.label.setText(_translate("DetailsResource", "Datei", None))
        self.browse_button.setText(_translate("DetailsResource", "...", None))

