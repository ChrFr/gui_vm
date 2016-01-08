# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_window.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
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

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(960, 766)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/buttons/icons/favicon.ico")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.splitter = QtGui.QSplitter(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 170, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(156, 156, 156))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        self.splitter.setPalette(palette)
        self.splitter.setFrameShape(QtGui.QFrame.NoFrame)
        self.splitter.setFrameShadow(QtGui.QFrame.Plain)
        self.splitter.setMidLineWidth(2)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setHandleWidth(2)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.layoutWidget = QtGui.QWidget(self.splitter)
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.gridLayout_4 = QtGui.QGridLayout()
        self.gridLayout_4.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        spacerItem = QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.gridLayout_4.addItem(spacerItem, 0, 3, 1, 2)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_4.addItem(spacerItem1, 0, 8, 1, 1)
        self.open_button = QtGui.QPushButton(self.layoutWidget)
        self.open_button.setMinimumSize(QtCore.QSize(0, 0))
        self.open_button.setMaximumSize(QtCore.QSize(30, 30))
        self.open_button.setText(_fromUtf8(""))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/buttons/icons/open.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.open_button.setIcon(icon1)
        self.open_button.setIconSize(QtCore.QSize(28, 28))
        self.open_button.setObjectName(_fromUtf8("open_button"))
        self.gridLayout_4.addWidget(self.open_button, 0, 0, 1, 1)
        self.context_button_group = QtGui.QGroupBox(self.layoutWidget)
        self.context_button_group.setMinimumSize(QtCore.QSize(265, 35))
        self.context_button_group.setTitle(_fromUtf8(""))
        self.context_button_group.setObjectName(_fromUtf8("context_button_group"))
        self.plus_button = QtGui.QToolButton(self.context_button_group)
        self.plus_button.setGeometry(QtCore.QRect(10, 5, 25, 25))
        self.plus_button.setText(_fromUtf8(""))
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/buttons/icons/plus.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.plus_button.setIcon(icon2)
        self.plus_button.setIconSize(QtCore.QSize(21, 21))
        self.plus_button.setObjectName(_fromUtf8("plus_button"))
        self.minus_button = QtGui.QToolButton(self.context_button_group)
        self.minus_button.setGeometry(QtCore.QRect(40, 5, 25, 25))
        self.minus_button.setText(_fromUtf8(""))
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(_fromUtf8(":/buttons/icons/minus.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.minus_button.setIcon(icon3)
        self.minus_button.setIconSize(QtCore.QSize(21, 21))
        self.minus_button.setObjectName(_fromUtf8("minus_button"))
        self.edit_button = QtGui.QPushButton(self.context_button_group)
        self.edit_button.setGeometry(QtCore.QRect(90, 5, 25, 25))
        self.edit_button.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.edit_button.setLocale(QtCore.QLocale(QtCore.QLocale.German, QtCore.QLocale.Germany))
        self.edit_button.setText(_fromUtf8(""))
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(_fromUtf8(":/buttons/icons/edit.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.edit_button.setIcon(icon4)
        self.edit_button.setIconSize(QtCore.QSize(21, 21))
        self.edit_button.setObjectName(_fromUtf8("edit_button"))
        self.reset_button = QtGui.QPushButton(self.context_button_group)
        self.reset_button.setGeometry(QtCore.QRect(120, 5, 25, 25))
        self.reset_button.setText(_fromUtf8(""))
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(_fromUtf8(":/buttons/icons/reset.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.reset_button.setIcon(icon5)
        self.reset_button.setIconSize(QtCore.QSize(21, 21))
        self.reset_button.setObjectName(_fromUtf8("reset_button"))
        self.lock_button = QtGui.QPushButton(self.context_button_group)
        self.lock_button.setGeometry(QtCore.QRect(230, 5, 25, 25))
        self.lock_button.setText(_fromUtf8(""))
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(_fromUtf8(":/buttons/icons/unlocked-yellow.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon6.addPixmap(QtGui.QPixmap(_fromUtf8(":/buttons/icons/locked-yellow.png")), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.lock_button.setIcon(icon6)
        self.lock_button.setIconSize(QtCore.QSize(19, 19))
        self.lock_button.setCheckable(True)
        self.lock_button.setObjectName(_fromUtf8("lock_button"))
        self.copy_button = QtGui.QPushButton(self.context_button_group)
        self.copy_button.setGeometry(QtCore.QRect(150, 5, 25, 25))
        self.copy_button.setText(_fromUtf8(""))
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(_fromUtf8(":/buttons/icons/copy.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.copy_button.setIcon(icon7)
        self.copy_button.setIconSize(QtCore.QSize(21, 21))
        self.copy_button.setObjectName(_fromUtf8("copy_button"))
        self.clean_button = QtGui.QPushButton(self.context_button_group)
        self.clean_button.setGeometry(QtCore.QRect(180, 5, 25, 25))
        self.clean_button.setText(_fromUtf8(""))
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap(_fromUtf8(":/buttons/icons/clean.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.clean_button.setIcon(icon8)
        self.clean_button.setIconSize(QtCore.QSize(22, 21))
        self.clean_button.setObjectName(_fromUtf8("clean_button"))
        self.gridLayout_4.addWidget(self.context_button_group, 0, 5, 1, 3)
        self.verticalLayout.addLayout(self.gridLayout_4)
        self.qtreeview = QtGui.QTreeView(self.layoutWidget)
        self.qtreeview.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.qtreeview.setExpandsOnDoubleClick(False)
        self.qtreeview.setObjectName(_fromUtf8("qtreeview"))
        self.verticalLayout.addWidget(self.qtreeview)
        self.layoutWidget1 = QtGui.QWidget(self.splitter)
        self.layoutWidget1.setObjectName(_fromUtf8("layoutWidget1"))
        self.details_layout = QtGui.QVBoxLayout(self.layoutWidget1)
        self.details_layout.setObjectName(_fromUtf8("details_layout"))
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.details_layout.addItem(spacerItem2)
        self.gridLayout.addWidget(self.splitter, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 960, 21))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuDatei = QtGui.QMenu(self.menubar)
        self.menuDatei.setObjectName(_fromUtf8("menuDatei"))
        self.menuHilfe = QtGui.QMenu(self.menubar)
        self.menuHilfe.setObjectName(_fromUtf8("menuHilfe"))
        self.menuProjekt = QtGui.QMenu(self.menubar)
        self.menuProjekt.setObjectName(_fromUtf8("menuProjekt"))
        self.menuZuletzt_benutzt = QtGui.QMenu(self.menuProjekt)
        self.menuZuletzt_benutzt.setObjectName(_fromUtf8("menuZuletzt_benutzt"))
        self.menuSzenario = QtGui.QMenu(self.menubar)
        self.menuSzenario.setObjectName(_fromUtf8("menuSzenario"))
        self.menuL_ufe = QtGui.QMenu(self.menubar)
        self.menuL_ufe.setObjectName(_fromUtf8("menuL_ufe"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.actionBeenden = QtGui.QAction(MainWindow)
        self.actionBeenden.setObjectName(_fromUtf8("actionBeenden"))
        self.actionProjekt_ffnen = QtGui.QAction(MainWindow)
        self.actionProjekt_ffnen.setObjectName(_fromUtf8("actionProjekt_ffnen"))
        self.actionProjekt_speichern = QtGui.QAction(MainWindow)
        self.actionProjekt_speichern.setObjectName(_fromUtf8("actionProjekt_speichern"))
        self.actionNeues_Projekt = QtGui.QAction(MainWindow)
        self.actionNeues_Projekt.setObjectName(_fromUtf8("actionNeues_Projekt"))
        self.actionNeues_Szenario = QtGui.QAction(MainWindow)
        self.actionNeues_Szenario.setObjectName(_fromUtf8("actionNeues_Szenario"))
        self.actionEinstellungen = QtGui.QAction(MainWindow)
        self.actionEinstellungen.setObjectName(_fromUtf8("actionEinstellungen"))
        self.actionInfo = QtGui.QAction(MainWindow)
        self.actionInfo.setObjectName(_fromUtf8("actionInfo"))
        self.actionSzenario_duplizieren = QtGui.QAction(MainWindow)
        self.actionSzenario_duplizieren.setObjectName(_fromUtf8("actionSzenario_duplizieren"))
        self.actionSzenario_l_schen = QtGui.QAction(MainWindow)
        self.actionSzenario_l_schen.setObjectName(_fromUtf8("actionSzenario_l_schen"))
        self.actionProjekt_schlie_en = QtGui.QAction(MainWindow)
        self.actionProjekt_schlie_en.setObjectName(_fromUtf8("actionProjekt_schlie_en"))
        self.actionBla = QtGui.QAction(MainWindow)
        self.actionBla.setObjectName(_fromUtf8("actionBla"))
        self.actionGesamtlauf_starten = QtGui.QAction(MainWindow)
        self.actionGesamtlauf_starten.setObjectName(_fromUtf8("actionGesamtlauf_starten"))
        self.actionSpezifischen_Lauf_anlegen = QtGui.QAction(MainWindow)
        self.actionSpezifischen_Lauf_anlegen.setObjectName(_fromUtf8("actionSpezifischen_Lauf_anlegen"))
        self.actionSpezifischen_Lauf_starten = QtGui.QAction(MainWindow)
        self.actionSpezifischen_Lauf_starten.setObjectName(_fromUtf8("actionSpezifischen_Lauf_starten"))
        self.menuDatei.addAction(self.actionEinstellungen)
        self.menuDatei.addSeparator()
        self.menuDatei.addAction(self.actionBeenden)
        self.menuHilfe.addAction(self.actionInfo)
        self.menuProjekt.addAction(self.actionNeues_Projekt)
        self.menuProjekt.addAction(self.actionProjekt_ffnen)
        self.menuProjekt.addAction(self.actionProjekt_schlie_en)
        self.menuProjekt.addSeparator()
        self.menuProjekt.addAction(self.menuZuletzt_benutzt.menuAction())
        self.menuSzenario.addAction(self.actionNeues_Szenario)
        self.menuSzenario.addAction(self.actionSzenario_duplizieren)
        self.menuSzenario.addAction(self.actionSzenario_l_schen)
        self.menuL_ufe.addAction(self.actionGesamtlauf_starten)
        self.menuL_ufe.addAction(self.actionSpezifischen_Lauf_anlegen)
        self.menuL_ufe.addAction(self.actionSpezifischen_Lauf_starten)
        self.menubar.addAction(self.menuDatei.menuAction())
        self.menubar.addAction(self.menuProjekt.menuAction())
        self.menubar.addAction(self.menuSzenario.menuAction())
        self.menubar.addAction(self.menuL_ufe.menuAction())
        self.menubar.addAction(self.menuHilfe.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "GGR Verkehrsmodelle", None))
        self.open_button.setToolTip(_translate("MainWindow", "Projekt öffnen", None))
        self.plus_button.setToolTip(_translate("MainWindow", "Hinzufügen", None))
        self.minus_button.setToolTip(_translate("MainWindow", "Entfernen", None))
        self.edit_button.setToolTip(_translate("MainWindow", "Umbenennen", None))
        self.reset_button.setToolTip(_translate("MainWindow", "Zurücksetzen", None))
        self.lock_button.setToolTip(_translate("MainWindow", "Zurücksetzen", None))
        self.copy_button.setToolTip(_translate("MainWindow", "Kopieren", None))
        self.clean_button.setToolTip(_translate("MainWindow", "Aufräumen", None))
        self.menuDatei.setTitle(_translate("MainWindow", "Datei", None))
        self.menuHilfe.setTitle(_translate("MainWindow", "Hilfe", None))
        self.menuProjekt.setTitle(_translate("MainWindow", "Projekt", None))
        self.menuZuletzt_benutzt.setTitle(_translate("MainWindow", "zuletzt benutzt", None))
        self.menuSzenario.setTitle(_translate("MainWindow", "Szenario", None))
        self.menuL_ufe.setTitle(_translate("MainWindow", "Läufe", None))
        self.actionBeenden.setText(_translate("MainWindow", "Beenden", None))
        self.actionProjekt_ffnen.setText(_translate("MainWindow", "Projekt öffnen", None))
        self.actionProjekt_speichern.setText(_translate("MainWindow", "Projekt speichern", None))
        self.actionNeues_Projekt.setText(_translate("MainWindow", "Neues Projekt", None))
        self.actionNeues_Szenario.setText(_translate("MainWindow", "Neues Szenario", None))
        self.actionEinstellungen.setText(_translate("MainWindow", "Einstellungen", None))
        self.actionInfo.setText(_translate("MainWindow", "Info", None))
        self.actionSzenario_duplizieren.setText(_translate("MainWindow", "Szenario duplizieren", None))
        self.actionSzenario_l_schen.setText(_translate("MainWindow", "Szenario löschen", None))
        self.actionProjekt_schlie_en.setText(_translate("MainWindow", "Projekt schließen", None))
        self.actionBla.setText(_translate("MainWindow", "bla", None))
        self.actionGesamtlauf_starten.setText(_translate("MainWindow", "Gesamtlauf starten", None))
        self.actionSpezifischen_Lauf_anlegen.setText(_translate("MainWindow", "spezifischen Lauf anlegen", None))
        self.actionSpezifischen_Lauf_starten.setText(_translate("MainWindow", "spezifischen Lauf starten", None))

import gui_rc
