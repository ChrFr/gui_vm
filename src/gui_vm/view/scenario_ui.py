# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'scenario.ui'
#
# Created: Mon Jan 12 16:53:01 2015
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

class Ui_DetailsScenario(object):
    def setupUi(self, DetailsScenario):
        DetailsScenario.setObjectName(_fromUtf8("DetailsScenario"))
        DetailsScenario.resize(450, 309)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(DetailsScenario.sizePolicy().hasHeightForWidth())
        DetailsScenario.setSizePolicy(sizePolicy)
        DetailsScenario.setMinimumSize(QtCore.QSize(450, 0))
        self.formLayoutWidget = QtGui.QWidget(DetailsScenario)
        self.formLayoutWidget.setGeometry(QtCore.QRect(10, 60, 391, 241))
        self.formLayoutWidget.setObjectName(_fromUtf8("formLayoutWidget"))
        self.formLayout = QtGui.QFormLayout(self.formLayoutWidget)
        self.formLayout.setSizeConstraint(QtGui.QLayout.SetMinimumSize)
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setMargin(0)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label = QtGui.QLabel(self.formLayoutWidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.combo_model = QtGui.QComboBox(self.formLayoutWidget)
        self.combo_model.setObjectName(_fromUtf8("combo_model"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.combo_model)
        self.start_button = QtGui.QPushButton(DetailsScenario)
        self.start_button.setGeometry(QtCore.QRect(10, 20, 100, 23))
        self.start_button.setMaximumSize(QtCore.QSize(100, 16777215))
        self.start_button.setObjectName(_fromUtf8("start_button"))

        self.retranslateUi(DetailsScenario)
        QtCore.QMetaObject.connectSlotsByName(DetailsScenario)

    def retranslateUi(self, DetailsScenario):
        DetailsScenario.setWindowTitle(_translate("DetailsScenario", "GroupBox", None))
        DetailsScenario.setTitle(_translate("DetailsScenario", "GroupBox", None))
        self.label.setText(_translate("DetailsScenario", "Verkehrsmodell", None))
        self.start_button.setText(_translate("DetailsScenario", "Gesamtlauf starten", None))

