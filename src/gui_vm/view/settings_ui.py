# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'settings.ui'
#
# Created: Tue Feb 24 17:01:15 2015
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
        self.maxemBox = QtGui.QGroupBox(self.models_tab)
        self.maxemBox.setGeometry(QtCore.QRect(10, 10, 571, 131))
        self.maxemBox.setObjectName(_fromUtf8("maxemBox"))
        self.gridLayoutWidget_2 = QtGui.QWidget(self.maxemBox)
        self.gridLayoutWidget_2.setGeometry(QtCore.QRect(10, 20, 551, 91))
        self.gridLayoutWidget_2.setObjectName(_fromUtf8("gridLayoutWidget_2"))
        self.gridLayout_3 = QtGui.QGridLayout(self.gridLayoutWidget_2)
        self.gridLayout_3.setMargin(0)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.label_4 = QtGui.QLabel(self.gridLayoutWidget_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)
        self.label_4.setMinimumSize(QtCore.QSize(0, 0))
        self.label_4.setMaximumSize(QtCore.QSize(10, 12))
        self.label_4.setText(_fromUtf8(""))
        self.label_4.setPixmap(QtGui.QPixmap(_fromUtf8(":/buttons/icons/fragezeichen.png")))
        self.label_4.setScaledContents(True)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout_3.addWidget(self.label_4, 0, 2, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_3.addItem(spacerItem1, 3, 1, 1, 1)
        self.maxem_exec_edit = QtGui.QLineEdit(self.gridLayoutWidget_2)
        self.maxem_exec_edit.setObjectName(_fromUtf8("maxem_exec_edit"))
        self.gridLayout_3.addWidget(self.maxem_exec_edit, 1, 1, 1, 1)
        self.maxem_default_edit = QtGui.QLineEdit(self.gridLayoutWidget_2)
        self.maxem_default_edit.setObjectName(_fromUtf8("maxem_default_edit"))
        self.gridLayout_3.addWidget(self.maxem_default_edit, 0, 1, 1, 1)
        self.label_3 = QtGui.QLabel(self.gridLayoutWidget_2)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout_3.addWidget(self.label_3, 0, 0, 1, 1)
        self.maxem_default_browse_button = QtGui.QPushButton(self.gridLayoutWidget_2)
        self.maxem_default_browse_button.setMaximumSize(QtCore.QSize(30, 16777215))
        self.maxem_default_browse_button.setObjectName(_fromUtf8("maxem_default_browse_button"))
        self.gridLayout_3.addWidget(self.maxem_default_browse_button, 0, 4, 1, 1)
        self.maxem_exec_browse_button = QtGui.QPushButton(self.gridLayoutWidget_2)
        self.maxem_exec_browse_button.setMaximumSize(QtCore.QSize(30, 16777215))
        self.maxem_exec_browse_button.setObjectName(_fromUtf8("maxem_exec_browse_button"))
        self.gridLayout_3.addWidget(self.maxem_exec_browse_button, 1, 4, 1, 1)
        self.label_5 = QtGui.QLabel(self.gridLayoutWidget_2)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout_3.addWidget(self.label_5, 1, 0, 1, 1)
        self.label_6 = QtGui.QLabel(self.gridLayoutWidget_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy)
        self.label_6.setMinimumSize(QtCore.QSize(0, 0))
        self.label_6.setMaximumSize(QtCore.QSize(10, 12))
        self.label_6.setText(_fromUtf8(""))
        self.label_6.setPixmap(QtGui.QPixmap(_fromUtf8(":/buttons/icons/fragezeichen.png")))
        self.label_6.setScaledContents(True)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout_3.addWidget(self.label_6, 1, 2, 1, 1)
        self.label_12 = QtGui.QLabel(self.gridLayoutWidget_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_12.sizePolicy().hasHeightForWidth())
        self.label_12.setSizePolicy(sizePolicy)
        self.label_12.setMinimumSize(QtCore.QSize(0, 0))
        self.label_12.setMaximumSize(QtCore.QSize(10, 12))
        self.label_12.setText(_fromUtf8(""))
        self.label_12.setPixmap(QtGui.QPixmap(_fromUtf8(":/buttons/icons/fragezeichen.png")))
        self.label_12.setScaledContents(True)
        self.label_12.setObjectName(_fromUtf8("label_12"))
        self.gridLayout_3.addWidget(self.label_12, 2, 2, 1, 1)
        self.python_edit = QtGui.QLineEdit(self.gridLayoutWidget_2)
        self.python_edit.setObjectName(_fromUtf8("python_edit"))
        self.gridLayout_3.addWidget(self.python_edit, 2, 1, 1, 1)
        self.python_exec_browse_button = QtGui.QPushButton(self.gridLayoutWidget_2)
        self.python_exec_browse_button.setMaximumSize(QtCore.QSize(30, 16777215))
        self.python_exec_browse_button.setObjectName(_fromUtf8("python_exec_browse_button"))
        self.gridLayout_3.addWidget(self.python_exec_browse_button, 2, 4, 1, 1)
        self.label_2 = QtGui.QLabel(self.gridLayoutWidget_2)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_3.addWidget(self.label_2, 2, 0, 1, 1)
        self.auto_python_button = QtGui.QPushButton(self.gridLayoutWidget_2)
        self.auto_python_button.setObjectName(_fromUtf8("auto_python_button"))
        self.gridLayout_3.addWidget(self.auto_python_button, 2, 5, 1, 1)
        self.verkmodBox = QtGui.QGroupBox(self.models_tab)
        self.verkmodBox.setEnabled(False)
        self.verkmodBox.setGeometry(QtCore.QRect(10, 150, 571, 121))
        self.verkmodBox.setObjectName(_fromUtf8("verkmodBox"))
        self.gridLayoutWidget_3 = QtGui.QWidget(self.verkmodBox)
        self.gridLayoutWidget_3.setGeometry(QtCore.QRect(10, 20, 551, 91))
        self.gridLayoutWidget_3.setObjectName(_fromUtf8("gridLayoutWidget_3"))
        self.gridLayout_4 = QtGui.QGridLayout(self.gridLayoutWidget_3)
        self.gridLayout_4.setMargin(0)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.verkmod_default_edit = QtGui.QLineEdit(self.gridLayoutWidget_3)
        self.verkmod_default_edit.setObjectName(_fromUtf8("verkmod_default_edit"))
        self.gridLayout_4.addWidget(self.verkmod_default_edit, 0, 2, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_4.addItem(spacerItem2, 2, 2, 1, 1)
        self.label_7 = QtGui.QLabel(self.gridLayoutWidget_3)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.gridLayout_4.addWidget(self.label_7, 0, 0, 1, 1)
        self.verkmod_default_browse_button = QtGui.QPushButton(self.gridLayoutWidget_3)
        self.verkmod_default_browse_button.setMaximumSize(QtCore.QSize(30, 16777215))
        self.verkmod_default_browse_button.setObjectName(_fromUtf8("verkmod_default_browse_button"))
        self.gridLayout_4.addWidget(self.verkmod_default_browse_button, 0, 3, 1, 1)
        self.verkmod_exec_edit = QtGui.QLineEdit(self.gridLayoutWidget_3)
        self.verkmod_exec_edit.setObjectName(_fromUtf8("verkmod_exec_edit"))
        self.gridLayout_4.addWidget(self.verkmod_exec_edit, 1, 2, 1, 1)
        self.verkmod_exec_browse_button = QtGui.QPushButton(self.gridLayoutWidget_3)
        self.verkmod_exec_browse_button.setMaximumSize(QtCore.QSize(30, 16777215))
        self.verkmod_exec_browse_button.setObjectName(_fromUtf8("verkmod_exec_browse_button"))
        self.gridLayout_4.addWidget(self.verkmod_exec_browse_button, 1, 3, 1, 1)
        self.label_8 = QtGui.QLabel(self.gridLayoutWidget_3)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.gridLayout_4.addWidget(self.label_8, 1, 0, 1, 1)
        self.label_9 = QtGui.QLabel(self.gridLayoutWidget_3)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_9.sizePolicy().hasHeightForWidth())
        self.label_9.setSizePolicy(sizePolicy)
        self.label_9.setMinimumSize(QtCore.QSize(0, 0))
        self.label_9.setMaximumSize(QtCore.QSize(10, 12))
        self.label_9.setText(_fromUtf8(""))
        self.label_9.setPixmap(QtGui.QPixmap(_fromUtf8(":/buttons/icons/fragezeichen.png")))
        self.label_9.setScaledContents(True)
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.gridLayout_4.addWidget(self.label_9, 0, 1, 1, 1)
        self.label_10 = QtGui.QLabel(self.gridLayoutWidget_3)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_10.sizePolicy().hasHeightForWidth())
        self.label_10.setSizePolicy(sizePolicy)
        self.label_10.setMinimumSize(QtCore.QSize(0, 0))
        self.label_10.setMaximumSize(QtCore.QSize(10, 12))
        self.label_10.setText(_fromUtf8(""))
        self.label_10.setPixmap(QtGui.QPixmap(_fromUtf8(":/buttons/icons/fragezeichen.png")))
        self.label_10.setScaledContents(True)
        self.label_10.setObjectName(_fromUtf8("label_10"))
        self.gridLayout_4.addWidget(self.label_10, 1, 1, 1, 1)
        self.tabWidget.addTab(self.models_tab, _fromUtf8(""))
        self.environment_tab = QtGui.QWidget()
        self.environment_tab.setObjectName(_fromUtf8("environment_tab"))
        self.gridLayoutWidget = QtGui.QWidget(self.environment_tab)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(10, 20, 581, 381))
        self.gridLayoutWidget.setObjectName(_fromUtf8("gridLayoutWidget"))
        self.gridLayout_2 = QtGui.QGridLayout(self.gridLayoutWidget)
        self.gridLayout_2.setMargin(0)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        spacerItem3 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem3, 2, 3, 1, 1)
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
        self.maxemBox.setTitle(_translate("Settings", "Maxem", None))
        self.label_4.setToolTip(_translate("Settings", "Der Ordner mit den Standard-Parameterdateien.", None))
        self.label_3.setText(_translate("Settings", "Defaultordner", None))
        self.maxem_default_browse_button.setText(_translate("Settings", "...", None))
        self.maxem_exec_browse_button.setText(_translate("Settings", "...", None))
        self.label_5.setText(_translate("Settings", "Programmdatei", None))
        self.label_6.setToolTip(_translate("Settings", "Der Pfad zum Pythonskript, mit dem das Verkehrsmodell ausgeführt wird.", None))
        self.label_12.setToolTip(_translate("Settings", "Der Pfad zum Python-Interpreter in dessen Umgebung das Verkehrsmodell kompiliert wurde.", None))
        self.python_exec_browse_button.setText(_translate("Settings", "...", None))
        self.label_2.setText(_translate("Settings", "Pythonpfad", None))
        self.auto_python_button.setText(_translate("Settings", "Auto", None))
        self.verkmodBox.setTitle(_translate("Settings", "VerkMod", None))
        self.label_7.setText(_translate("Settings", "Defaultordner", None))
        self.verkmod_default_browse_button.setText(_translate("Settings", "...", None))
        self.verkmod_exec_browse_button.setText(_translate("Settings", "...", None))
        self.label_8.setText(_translate("Settings", "Programmdatei", None))
        self.label_9.setToolTip(_translate("Settings", "Der Ordner mit den Standard-Parameterdateien.", None))
        self.label_10.setToolTip(_translate("Settings", "Der Pfad zur Datei, mit der das Verkehrsmodell ausgeführt wird.", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.models_tab), _translate("Settings", "Verkehrsmodelle", None))
        self.hdf5_exec_browse_button.setText(_translate("Settings", "...", None))
        self.label_11.setText(_translate("Settings", "HDF5 Viewer", None))
        self.label_13.setToolTip(_translate("Settings", "Der Pfad zur ausführbaren Datei eines HDF5 Viewers.", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.environment_tab), _translate("Settings", "Umgebung", None))

import gui_rc
