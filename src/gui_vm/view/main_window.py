# -*- coding: utf-8 -*-
import sys, os
from gui_vm.view.qt_designed.main_window_ui import Ui_MainWindow
from PyQt4 import QtGui, QtCore
from project_view import ProjectTreeView
from gui_vm.view.dialogs import NewProjectDialog, SettingsDialog
from gui_vm.view.qt_designed.welcome_ui import Ui_Welcome
from gui_vm.config.config import Config

config = Config()
config.read()

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s


class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
    project_changed = QtCore.pyqtSignal()

    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.setupUi(self)

        # define the view on the project and connect to the qtreeview in
        # the main window
        self.project_view = ProjectTreeView(parent=self)
        self.qtreeview.setModel(self.project_view)
        self.qtreeview.clicked[QtCore.QModelIndex].connect(
            self.project_view.item_clicked)

        self.qtreeview.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.qtreeview.customContextMenuRequested.connect(self.project_view.pop_context_menu)

        self.project_has_changed = False

        # connect the buttons
        self.plus_button.clicked.connect(self.project_view.add)
        self.minus_button.clicked.connect(self.project_view.remove)
        self.edit_button.clicked.connect(self.project_view.edit)
        self.reset_button.clicked.connect(self.project_view.reset)
        self.save_button.clicked.connect(self.save_project)
        self.open_button.clicked.connect(self.load_project)
        self.start_button.clicked.connect(self.project_view.run)
        self.reload_button.clicked.connect(self.project_view.do_reload)

        # activation of buttons depending on the selected item
        self.project_view.editable[bool].connect(
            self.edit_button.setEnabled)
        self.project_view.addable[bool].connect(
            self.plus_button.setEnabled)
        self.project_view.removable[bool].connect(
            self.minus_button.setEnabled)
        self.project_view.resetable[bool].connect(
            self.reset_button.setEnabled)
        self.project_view.reloadable[bool].connect(
            self.reload_button.setEnabled)

        for button in self.context_button_group.children():
            button.setEnabled(False)
        self.start_button.setEnabled(True)
        #self.project_view.refreshable[bool].connect(
            #self.edit_button.setEnabled)

        # connect the tool bar
        self.actionProjekt_speichern.triggered.connect(self.save_project)
        self.actionProjekt_ffnen.triggered.connect(self.load_project)
        self.actionNeues_Szenario.triggered.connect(
            self.project_view.add_run)
        self.actionNeues_Projekt.triggered.connect(self.create_project)
        self.actionEinstellungen.triggered.connect(self.edit_settings)
        self.actionBeenden.triggered.connect(QtGui.qApp.quit)

        self.project_view.dataChanged.connect(self.update_gui)
        self.project_view.view_changed.connect(self.update_gui)
        self.project_view.project_changed.connect(self.project_changed_handler)
        self.project_changed.connect(self.project_changed_handler)
        welcome = WelcomeDialog(self)

    def update_gui(self):
        '''
        refresh the view on the project tree
        '''
        self.qtreeview.expandAll()
        for column in range(self.qtreeview.model()
                            .columnCount(QtCore.QModelIndex())):
            self.qtreeview.resizeColumnToContents(column)
        self.project_view.refresh_details()
        details = self.project_view.details
        if details is not None:
            self.details_layout.addWidget(details)
            details.show()

    def create_project(self):
        '''
        create a new project
        return True if new project was created
        '''
        (project_name, project_folder, ok) = NewProjectDialog.getValues()
        if ok:
            do_continue = True
            if self.project_has_changed:
                do_continue = self.project_changed_message()
            if do_continue:
                self.project_view.create_project(project_name, project_folder)
                self.project_has_changed = False
                return True
        else:
            return False

    def edit_settings(self):
        SettingsDialog(self)

    def load_project(self):
        '''
        load a project
        return True if project was loaded
        '''
        fileinput = str(QtGui.QFileDialog.getOpenFileName(
            self, _fromUtf8('Projekt öffnen'), config.settings['environment']['default_project_folder'], '*.xml'))
        if len(fileinput) > 0:
            do_continue = True
            if self.project_has_changed:
                do_continue = self.project_changed_message()
            if do_continue:
                self.project_view.read_project(fileinput)
                self.project_has_changed = False
                return True
        return False

    def save_project(self):
        '''
        save the project
        return True if project was saved
        '''
        filename = str(QtGui.QFileDialog.getSaveFileName(
            self, 'Projekt speichern', '.', '*.xml'))
        #filename is '' if aborted (file dialog returns no status)
        if len(filename) > 0:
            self.project_view.write_project(filename)
            QtGui.QMessageBox.about(
                self, "Speichern erfolgreich",
                'Die Speicherung des Projektes\n{}\n war erfolgreich'.
                format(filename))
            self.project_has_changed = False
            return True
        return False

    def project_changed_handler(self):
        '''
        handle what happens, if project has changed
        '''
        self.project_has_changed = True
        self.update_gui()

    def project_changed_message(self):
        '''
        popup a message to save the project or not (due to changes)
        '''
        do_continue = False
        dialog = QtGui.QMessageBox()
        reply = dialog.question(
            self, _fromUtf8("Projekt geändert"),
            _fromUtf8('Das Projekt wurde geändert.\n' +
                      'Wollen Sie die Änderungen speichern?'),
            QtGui.QMessageBox.Save, QtGui.QMessageBox.Discard,
            QtGui.QMessageBox.Cancel)
        if reply == QtGui.QMessageBox.Save:
            saved = self.save_project()
            if saved:
                do_continue = True
            else:
                do_continue = False
        elif reply == QtGui.QMessageBox.Discard:
            do_continue = True
        return do_continue

    def closeEvent(self, event):
        do_continue = True
        if self.project_has_changed:
            do_continue = self.project_changed_message()
        if do_continue:
            event.accept()
        else:
            event.ignore()


class WelcomeDialog(QtGui.QDialog, Ui_Welcome):
    '''
    open a dialog to set the project name and folder and afterwards create
    a new project
    '''

    def __init__(self, parent):
        super(WelcomeDialog, self).__init__(parent=parent)
        self.parent = parent
        self.setupUi(self)
        self.exit_button.clicked.connect(QtGui.qApp.quit)
        self.open_button.clicked.connect(self.load_project)
        self.new_button.clicked.connect(self.create_project)
        self.cancel_button.clicked.connect(self.close)
        self.show()

    def load_project(self):
        loaded = self.parent.load_project()
        if loaded:
            self.close()

    def create_project(self):
        created = self.parent.create_project()
        if created:
            self.close()

