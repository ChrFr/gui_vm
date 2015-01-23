# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'special_run.ui'
#
# Created: Fri Jan 23 10:13:11 2015
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

class Ui_SpecialRun(object):
    def setupUi(self, SpecialRun):
        SpecialRun.setObjectName(_fromUtf8("SpecialRun"))
        SpecialRun.resize(372, 362)
        self.gridLayout = QtGui.QGridLayout(SpecialRun)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.store_button = QtGui.QPushButton(SpecialRun)
        self.store_button.setObjectName(_fromUtf8("store_button"))
        self.horizontalLayout.addWidget(self.store_button)
        self.start_button = QtGui.QPushButton(SpecialRun)
        self.start_button.setObjectName(_fromUtf8("start_button"))
        self.horizontalLayout.addWidget(self.start_button)
        self.cancel_button = QtGui.QPushButton(SpecialRun)
        self.cancel_button.setObjectName(_fromUtf8("cancel_button"))
        self.horizontalLayout.addWidget(self.cancel_button)
        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 1)
        self.tabWidget = QtGui.QTabWidget(SpecialRun)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.area_types = QtGui.QWidget()
        self.area_types.setObjectName(_fromUtf8("area_types"))
        self.gridLayout_2 = QtGui.QGridLayout(self.area_types)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.scroll_area_types = QtGui.QScrollArea(self.area_types)
        self.scroll_area_types.setWidgetResizable(True)
        self.scroll_area_types.setObjectName(_fromUtf8("scroll_area_types"))
        self.scrollAreaWidgetContents_3 = QtGui.QWidget()
        self.scrollAreaWidgetContents_3.setGeometry(QtCore.QRect(0, 0, 328, 267))
        self.scrollAreaWidgetContents_3.setObjectName(_fromUtf8("scrollAreaWidgetContents_3"))
        self.scroll_area_types.setWidget(self.scrollAreaWidgetContents_3)
        self.gridLayout_2.addWidget(self.scroll_area_types, 0, 0, 1, 1)
        self.tabWidget.addTab(self.area_types, _fromUtf8(""))
        self.activities = QtGui.QWidget()
        self.activities.setObjectName(_fromUtf8("activities"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.activities)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.scroll_activities = QtGui.QScrollArea(self.activities)
        self.scroll_activities.setWidgetResizable(True)
        self.scroll_activities.setObjectName(_fromUtf8("scroll_activities"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 328, 267))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.scroll_activities.setWidget(self.scrollAreaWidgetContents)
        self.horizontalLayout_2.addWidget(self.scroll_activities)
        self.tabWidget.addTab(self.activities, _fromUtf8(""))
        self.persons = QtGui.QWidget()
        self.persons.setObjectName(_fromUtf8("persons"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self.persons)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.scroll_persons = QtGui.QScrollArea(self.persons)
        self.scroll_persons.setWidgetResizable(True)
        self.scroll_persons.setObjectName(_fromUtf8("scroll_persons"))
        self.scrollAreaWidgetContents_2 = QtGui.QWidget()
        self.scrollAreaWidgetContents_2.setGeometry(QtCore.QRect(0, 0, 328, 267))
        self.scrollAreaWidgetContents_2.setObjectName(_fromUtf8("scrollAreaWidgetContents_2"))
        self.scroll_persons.setWidget(self.scrollAreaWidgetContents_2)
        self.horizontalLayout_3.addWidget(self.scroll_persons)
        self.tabWidget.addTab(self.persons, _fromUtf8(""))
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)

        self.retranslateUi(SpecialRun)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(SpecialRun)

    def retranslateUi(self, SpecialRun):
        SpecialRun.setWindowTitle(_translate("SpecialRun", "Sonderauswertung", None))
        self.store_button.setText(_translate("SpecialRun", "Speichern", None))
        self.start_button.setText(_translate("SpecialRun", "Starten", None))
        self.cancel_button.setText(_translate("SpecialRun", "Abbrechen", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.area_types), _translate("SpecialRun", "Gebietstypen", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.activities), _translate("SpecialRun", "Aktivitäten", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.persons), _translate("SpecialRun", "Personengruppen", None))

