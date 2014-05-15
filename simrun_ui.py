# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'simrun.ui'
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

class Ui_DetailsSimRun(object):
    def setupUi(self, DetailsSimRun):
        DetailsSimRun.setObjectName(_fromUtf8("DetailsSimRun"))
        DetailsSimRun.resize(411, 309)
        self.formLayoutWidget = QtGui.QWidget(DetailsSimRun)
        self.formLayoutWidget.setGeometry(QtCore.QRect(10, 20, 391, 281))
        self.formLayoutWidget.setObjectName(_fromUtf8("formLayoutWidget"))
        self.formLayout = QtGui.QFormLayout(self.formLayoutWidget)
        self.formLayout.setMargin(0)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.combo_model = QtGui.QComboBox(self.formLayoutWidget)
        self.combo_model.setObjectName(_fromUtf8("combo_model"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.combo_model)
        self.label = QtGui.QLabel(self.formLayoutWidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)

        self.retranslateUi(DetailsSimRun)
        QtCore.QMetaObject.connectSlotsByName(DetailsSimRun)

    def retranslateUi(self, DetailsSimRun):
        DetailsSimRun.setWindowTitle(_translate("DetailsSimRun", "GroupBox", None))
        DetailsSimRun.setTitle(_translate("DetailsSimRun", "GroupBox", None))
        self.label.setText(_translate("DetailsSimRun", "Verkehrsmodell", None))

