# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'project.ui'
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

class Ui_DetailsProject(object):
    def setupUi(self, DetailsProject):
        DetailsProject.setObjectName(_fromUtf8("DetailsProject"))
        DetailsProject.resize(394, 406)
        self.formLayoutWidget = QtGui.QWidget(DetailsProject)
        self.formLayoutWidget.setGeometry(QtCore.QRect(10, 20, 371, 371))
        self.formLayoutWidget.setObjectName(_fromUtf8("formLayoutWidget"))
        self.meta_layout = QtGui.QFormLayout(self.formLayoutWidget)
        self.meta_layout.setMargin(0)
        self.meta_layout.setObjectName(_fromUtf8("meta_layout"))

        self.retranslateUi(DetailsProject)
        QtCore.QMetaObject.connectSlotsByName(DetailsProject)

    def retranslateUi(self, DetailsProject):
        DetailsProject.setWindowTitle(_translate("DetailsProject", "GroupBox", None))
        DetailsProject.setTitle(_translate("DetailsProject", "GroupBox", None))

