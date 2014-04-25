# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'resource.ui'
#
# Created: Fri Apr 25 17:10:26 2014
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
        DetailsResource.resize(511, 444)
        self.verticalLayout_2 = QtGui.QVBoxLayout(DetailsResource)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.pushButton = QtGui.QPushButton(DetailsResource)
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.gridLayout.addWidget(self.pushButton, 4, 2, 1, 1)
        self.file_edit = QtGui.QLineEdit(DetailsResource)
        self.file_edit.setObjectName(_fromUtf8("file_edit"))
        self.gridLayout.addWidget(self.file_edit, 1, 1, 1, 1)
        self.browse_button = QtGui.QPushButton(DetailsResource)
        self.browse_button.setMaximumSize(QtCore.QSize(30, 30))
        self.browse_button.setObjectName(_fromUtf8("browse_button"))
        self.gridLayout.addWidget(self.browse_button, 1, 2, 1, 1)
        self.label = QtGui.QLabel(DetailsResource)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.project_copy = QtGui.QLineEdit(DetailsResource)
        self.project_copy.setReadOnly(True)
        self.project_copy.setObjectName(_fromUtf8("project_copy"))
        self.gridLayout.addWidget(self.project_copy, 0, 1, 1, 1)
        self.label_2 = QtGui.QLabel(DetailsResource)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.attribute_view = QtGui.QTableWidget(DetailsResource)
        self.attribute_view.setShowGrid(True)
        self.attribute_view.setObjectName(_fromUtf8("attribute_view"))
        self.attribute_view.setColumnCount(0)
        self.attribute_view.setRowCount(0)
        self.attribute_view.horizontalHeader().setVisible(True)
        self.attribute_view.horizontalHeader().setHighlightSections(True)
        self.attribute_view.verticalHeader().setVisible(False)
        self.attribute_view.verticalHeader().setHighlightSections(False)
        self.gridLayout.addWidget(self.attribute_view, 3, 0, 1, 3)
        self.verticalLayout_2.addLayout(self.gridLayout)

        self.retranslateUi(DetailsResource)
        QtCore.QMetaObject.connectSlotsByName(DetailsResource)

    def retranslateUi(self, DetailsResource):
        DetailsResource.setWindowTitle(_translate("DetailsResource", "GroupBox", None))
        DetailsResource.setTitle(_translate("DetailsResource", "GroupBox", None))
        self.pushButton.setText(_translate("DetailsResource", "Status prüfen", None))
        self.browse_button.setText(_translate("DetailsResource", "...", None))
        self.label.setText(_translate("DetailsResource", "Quelle", None))
        self.label_2.setText(_translate("DetailsResource", "Projektdatei", None))

