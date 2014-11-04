# -*- coding: utf-8 -*-
import sys
from gui_vm.view.qt_designed.main_window_ui import Ui_MainWindow
from PyQt4 import QtGui, QtCore
from project_view import ProjectTreeView
from gui_vm.view.qt_designed.new_project_ui import Ui_NewProject
from gui_vm.view.qt_designed.welcome_ui import Ui_Welcome
from gui_vm.view.qt_designed.settings_ui import Ui_Settings
from gui_vm.config.config import Config
import os

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

        self.config = Config()
        self.config.read()
        #define the view on the project and connect to the qtreeview in
        #the main window
        self.project_view = ProjectTreeView(parent=self)
        self.qtreeview.setModel(self.project_view)
        self.qtreeview.clicked[QtCore.QModelIndex].connect(
            self.project_view.item_clicked)
        self.project_has_changed = False

        #connect the buttons
        self.plus_button.clicked.connect(self.project_view.add)
        self.minus_button.clicked.connect(self.project_view.remove)
        self.edit_button.clicked.connect(self.project_view.edit)
        self.reset_button.clicked.connect(self.project_view.reset)
        self.save_button.clicked.connect(self.save_project)
        self.open_button.clicked.connect(self.load_project)
        self.start_button.clicked.connect(self.project_view.run)
        self.reload_button.clicked.connect(self.project_view.do_reload)

        #activation of buttons depending on the selected item
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

        #connect the tool bar
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
        project_name, project_folder, ok = NewProjectDialog.getValues()
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
        '''
        create a new project
        return True if new project was created
        '''
        SettingsDialog(self)

    def load_project(self):
        '''
        load a project
        return True if project was loaded
        '''
        fileinput = str(QtGui.QFileDialog.getOpenFileName(
            self, _fromUtf8('Projekt öffnen'), '.', '*.xml'))
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


class NewProjectDialog(QtGui.QDialog, Ui_NewProject):
    '''
    open a dialog to set the project name and folder and afterwards create
    a new project
    '''

    def __init__(self, parent=None):
        super(NewProjectDialog, self).__init__(parent)
        self.setupUi(self)
        self.folder_browse_button.clicked.connect(self.browse_folder)
        self.show()

    def browse_folder(self):
        '''
        open a file browser to set the project folder
        '''
        folder = str(
            QtGui.QFileDialog.getExistingDirectory(
                self, 'Projektverzeichnis wählen', '.'))
        #filename is '' if canceled
        if len(folder) > 0:
            self.folder_edit.setText(folder)

    @staticmethod
    def getValues():
        dialog = NewProjectDialog()
        ok = dialog.exec_()
        project_name = str(dialog.project_edit.text())
        project_folder = str(dialog.folder_edit.text())
        if ok == QtGui.QDialog.Accepted:
            if os.path.exists(project_folder):
                return (project_name, project_folder,
                        True)
            else:
                QtGui.QMessageBox.about(
                    dialog, "Warnung!", "Verzeichnis {} existiert nicht!"
                    .format(project_folder))
        return (project_name, project_folder, False)

class SettingsDialog(QtGui.QDialog, Ui_Settings):
    '''
    open a dialog to set the project name and folder and afterwards create
    a new project
    '''

    def __init__(self, parent=None):
        super(SettingsDialog, self).__init__(parent)
        self.setupUi(self)
        self.config = parent.config

        env = self.config.settings['environment']
        self.project_edit.setText(env['default_project_folder'])
        self.project_browse_button.clicked.connect(
            lambda: self.set_folder(self.project_edit))

        self.python_edit.setText(env['python_path'])
        self.python_exec_browse_button.clicked.connect(
            lambda: self.set_file(self.python_edit, 'python.exe'))

        mod = self.config.settings['trafficmodels']
        maxem = mod['Maxem']
        self.maxem_default_edit.setText(maxem['default_folder'])
        self.maxem_default_browse_button.clicked.connect(
            lambda: self.set_folder(self.maxem_default_edit))
        self.maxem_exec_edit.setText(maxem['executable'])
        self.maxem_exec_browse_button.clicked.connect(
            lambda: self.set_file(self.maxem_exec_edit, '*.py'))

        verkmod = mod['VerkMod']
        self.verkmod_default_edit.setText(verkmod['default_folder'])
        self.verkmod_default_browse_button.clicked.connect(
            lambda: self.set_folder(self.verkmod_default_edit))
        self.verkmod_exec_edit.setText(verkmod['executable'])
        self.verkmod_exec_browse_button.clicked.connect(
            lambda: self.set_file(self.verkmod_exec_edit, '*.exe'))

        self.OK_button.clicked.connect(self.write_config)
        self.reset_button.clicked.connect(self.reset)
        self.cancel_button.clicked.connect(self.close)
        self.show()

    def set_file(self, line_edit, extension):
        '''
        open a file browser to put a path to a file into the given line edit
        '''
        filename = str(
            QtGui.QFileDialog.getOpenFileName(
                self, 'Datei wählen', extension))
        #filename is '' if canceled
        if len(filename) > 0:
            line_edit.setText(filename)

    def set_folder(self, line_edit):
        '''
        open a file browser to put a directory into the given line edit
        '''
        folder = str(
            QtGui.QFileDialog.getExistingDirectory(
                self, 'Ordner wählen', '.'))
        #folder is '' if canceled
        if len(folder) > 0:
            line_edit.setText(folder)

    def write_config(self):
        env = self.config.settings['environment']
        env['default_project_folder'] = str(self.project_edit.text())
        env['python_path'] = str(self.python_edit.text())

        mod = self.config.settings['trafficmodels']
        maxem = mod['Maxem']
        maxem['default_folder'] = str(self.maxem_default_edit.text())
        maxem['executable'] = str(self.maxem_exec_edit.text())

        verkmod = mod['VerkMod']
        verkmod['default_folder'] = str(self.verkmod_default_edit.text())
        verkmod['executable'] = str(self.verkmod_exec_edit.text())

        self.config.write()
        self.close()

    def reset(self):
        pass


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
