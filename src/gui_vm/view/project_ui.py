# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'project.ui'
#
# Created: Wed May 11 15:58:10 2016
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
        self.label = QtGui.QLabel(self.gridLayoutWidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.gridLayout.addItem(spacerItem, 1, 0, 1, 1)
        self.meta_layout = QtGui.QFormLayout()
        self.meta_layout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.meta_layout.setContentsMargins(-1, -1, 9, -1)
        self.meta_layout.setObjectName(_fromUtf8("meta_layout"))
        self.gridLayout.addLayout(self.meta_layout, 4, 0, 1, 3)
        self.label_2 = QtGui.QLabel(self.gridLayoutWidget)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 3, 0, 1, 1)
        self.folder_edit = QtGui.QLineEdit(self.gridLayoutWidget)
        self.folder_edit.setReadOnly(True)
        self.folder_edit.setObjectName(_fromUtf8("folder_edit"))
        self.gridLayout.addWidget(self.folder_edit, 0, 1, 1, 2)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 3, 1, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.add_meta_button = QtGui.QPushButton(self.gridLayoutWidget)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/buttons/icons/plus.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.add_meta_button.setIcon(icon)
        self.add_meta_button.setObjectName(_fromUtf8("add_meta_button"))
        self.horizontalLayout.addWidget(self.add_meta_button)
        self.gridLayout.addLayout(self.horizontalLayout, 5, 1, 1, 1)
        spacerItem3 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem3, 6, 1, 1, 1)

        self.retranslateUi(DetailsProject)
        QtCore.QMetaObject.connectSlotsByName(DetailsProject)

    def retranslateUi(self, DetailsProject):
        DetailsProject.setWindowTitle(_translate("DetailsProject", "GroupBox", None))
        DetailsProject.setTitle(_translate("DetailsProject", "GroupBox", None))
        self.label.setText(_translate("DetailsProject", "Projektordner", None))
        self.label_2.setText(_translate("DetailsProject", "Metadaten:", None))
        self.add_meta_button.setText(_translate("DetailsProject", "Feld hinzu", None))

import gui_rc
