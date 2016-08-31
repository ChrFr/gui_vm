# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'settings.ui'
#
# Created: Wed Aug 31 13:00:45 2016
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

class Ui_Settings(object):
    def setupUi(self, Settings):
        Settings.setObjectName(_fromUtf8("Settings"))
        Settings.resize(623, 483)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Settings.sizePolicy().hasHeightForWidth())
        Settings.setSizePolicy(sizePolicy)
        Settings.setMinimumSize(QtCore.QSize(623, 483))
        Settings.setMaximumSize(QtCore.QSize(623, 483))
        Settings.setSizeGripEnabled(False)
        Settings.setModal(True)
        self.gridLayout = QtGui.QGridLayout(Settings)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.OK_button = QtGui.QPushButton(Settings)
        self.OK_button.setObjectName(_fromUtf8("OK_button"))
        self.horizontalLayout.addWidget(self.OK_button)
        self.reset_button = QtGui.QPushButton(Settings)
        self.reset_button.setObjectName(_fromUtf8("reset_button"))
        self.horizontalLayout.addWidget(self.reset_button)
        self.cancel_button = QtGui.QPushButton(Settings)
        self.cancel_button.setObjectName(_fromUtf8("cancel_button"))
        self.horizontalLayout.addWidget(self.cancel_button)
        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 1)
        self.tabWidget = QtGui.QTabWidget(Settings)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.models_tab = QtGui.QWidget()
        self.models_tab.setObjectName(_fromUtf8("models_tab"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.models_tab)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.auto_check = QtGui.QCheckBox(self.models_tab)
        self.auto_check.setObjectName(_fromUtf8("auto_check"))
        self.verticalLayout_2.addWidget(self.auto_check)
        self.scrollArea = QtGui.QScrollArea(self.models_tab)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.models_scroll_content = QtGui.QWidget()
        self.models_scroll_content.setGeometry(QtCore.QRect(0, 0, 579, 365))
        self.models_scroll_content.setObjectName(_fromUtf8("models_scroll_content"))
        self.scrollArea.setWidget(self.models_scroll_content)
        self.verticalLayout_2.addWidget(self.scrollArea)
        self.tabWidget.addTab(self.models_tab, _fromUtf8(""))
        self.environment_tab = QtGui.QWidget()
        self.environment_tab.setObjectName(_fromUtf8("environment_tab"))
        self.gridLayoutWidget = QtGui.QWidget(self.environment_tab)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(10, 20, 581, 381))
        self.gridLayoutWidget.setObjectName(_fromUtf8("gridLayoutWidget"))
        self.gridLayout_2 = QtGui.QGridLayout(self.gridLayoutWidget)
        self.gridLayout_2.setMargin(0)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem1, 2, 3, 1, 1)
        self.hdf5_exec_browse_button = QtGui.QPushButton(self.gridLayoutWidget)
        self.hdf5_exec_browse_button.setMaximumSize(QtCore.QSize(30, 16777215))
        self.hdf5_exec_browse_button.setObjectName(_fromUtf8("hdf5_exec_browse_button"))
        self.gridLayout_2.addWidget(self.hdf5_exec_browse_button, 1, 5, 1, 1)
        self.hdf5_edit = QtGui.QLineEdit(self.gridLayoutWidget)
        self.hdf5_edit.setObjectName(_fromUtf8("hdf5_edit"))
        self.gridLayout_2.addWidget(self.hdf5_edit, 1, 3, 1, 1)
        self.label_11 = QtGui.QLabel(self.gridLayoutWidget)
        self.label_11.setObjectName(_fromUtf8("label_11"))
        self.gridLayout_2.addWidget(self.label_11, 1, 0, 1, 1)
        self.label_13 = QtGui.QLabel(self.gridLayoutWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_13.sizePolicy().hasHeightForWidth())
        self.label_13.setSizePolicy(sizePolicy)
        self.label_13.setMinimumSize(QtCore.QSize(0, 0))
        self.label_13.setMaximumSize(QtCore.QSize(10, 12))
        self.label_13.setText(_fromUtf8(""))
        self.label_13.setPixmap(QtGui.QPixmap(_fromUtf8(":/buttons/icons/fragezeichen.png")))
        self.label_13.setScaledContents(True)
        self.label_13.setObjectName(_fromUtf8("label_13"))
        self.gridLayout_2.addWidget(self.label_13, 1, 4, 1, 1)
        self.tabWidget.addTab(self.environment_tab, _fromUtf8(""))
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)

        self.retranslateUi(Settings)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Settings)

    def retranslateUi(self, Settings):
        Settings.setWindowTitle(_translate("Settings", "Einstellungen", None))
        self.OK_button.setText(_translate("Settings", "OK", None))
        self.reset_button.setText(_translate("Settings", "Zurücksetzen", None))
        self.cancel_button.setText(_translate("Settings", "Abbrechen", None))
        self.auto_check.setToolTip(_translate("Settings", "bei Aktivierung wird automatisch bei Start und Änderung von Ressourcen \n"
"Korrektheit der Eingabedaten geprüft", None))
        self.auto_check.setText(_translate("Settings", "automatische Prüfung an/aus", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.models_tab), _translate("Settings", "Verkehrsmodelle", None))
        self.hdf5_exec_browse_button.setText(_translate("Settings", "...", None))
        self.label_11.setText(_translate("Settings", "HDF5 Viewer", None))
        self.label_13.setToolTip(_translate("Settings", "Der Pfad zur ausführbaren Datei eines HDF5 Viewers.", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.environment_tab), _translate("Settings", "Umgebung", None))

import gui_rc
