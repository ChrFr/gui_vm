# -*- coding: utf-8 -*-
import sys, os
from functools import partial
from gui_vm.view.main_window_ui import Ui_MainWindow
from gui_vm.view.welcome_ui import Ui_Welcome
from PyQt4 import QtGui, QtCore
from gui_vm.control.project_control import VMProjectControl
from gui_vm.model.project_tree import Project
from gui_vm.control.dialogs import NewProjectDialog, SettingsDialog
from gui_vm.config.config import Config
from gui_vm.model.project_tree import TreeNode

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
        self.project_tree = TreeNode('root')
        self.project_control = VMProjectControl(view=self.qtreeview)
        self.qtreeview.setModel(self.project_control)
        self.qtreeview.clicked[QtCore.QModelIndex].connect(
            self.project_control.item_clicked)

        self.qtreeview.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.qtreeview.customContextMenuRequested.connect(
            self.project_control.pop_context_menu)

        self.project_has_changed = False
        self.recently_used_actions = []

        self.actionProjekt_ffnen.triggered.connect(self.load_project)
        self.open_button.clicked.connect(self.load_project)

        # connect the context buttons with the project control
        self.plus_button.clicked.connect(self.project_control.add)
        self.minus_button.clicked.connect(self.project_control.remove)
        self.edit_button.clicked.connect(self.project_control.edit)
        self.reset_button.clicked.connect(self.project_control.reset)
        self.start_button.clicked.connect(self.project_control.execute)
        self.lock_button.clicked.connect(self.project_control.switch_lock)

        # activation of buttons depending on the selected item
        self.project_control.editable[bool].connect(
            self.edit_button.setEnabled)
        self.project_control.addable[bool].connect(
            self.plus_button.setEnabled)
        self.project_control.removable[bool].connect(
            self.minus_button.setEnabled)
        self.project_control.resetable[bool].connect(
            self.reset_button.setEnabled)
        self.project_control.executable[bool].connect(
            self.start_button.setEnabled)
        self.project_control.lockable[bool].connect(
            self.switch_lock)

        #self.lock_button.sets

        for button in self.context_button_group.children():
            button.setEnabled(False)
        self.start_button.setEnabled(False)

        # connect the menubar
        self.actionNeues_Szenario.triggered.connect(
            self.project_control.add_scenario)
        self.actionNeues_Projekt.triggered.connect(self.create_project)
        self.actionEinstellungen.triggered.connect(self.edit_settings)
        self.actionBeenden.triggered.connect(QtGui.qApp.quit)

        self.project_control.dataChanged.connect(self.update_gui)
        self.project_control.view_changed.connect(self.update_gui)
        self.project_control.project_changed.connect(self.project_changed_handler)
        self.project_changed.connect(self.project_changed_handler)
        #open recent project
        h = config.settings['history']
        if len(h) > 0:
            for recent in h:
                action = QtGui.QAction(self)
                action.setText(_fromUtf8(recent))
                self.recently_used_actions.append(action)
                self.menuZuletzt_benutzt.addAction(action)
                project_file = os.path.join(recent, Project.FILENAME_DEFAULT)
                action.triggered.connect(partial((lambda filename: self.project_control.read_project(filename)), project_file))

            project_file = os.path.join(h[0], Project.FILENAME_DEFAULT)
            if os.path.isfile(project_file):
                self.project_control.read_project(project_file)
        #welcome screen if there is none (assumed first start)
        else:
            welcome = WelcomeDialog(self)

    def update_gui(self):
        '''
        refresh the view on the project tree
        '''
        self.qtreeview.expandAll()
        for column in range(self.qtreeview.model()
                            .columnCount(QtCore.QModelIndex())):
            self.qtreeview.resizeColumnToContents(column)
        self.project_control.update_details(self.details_layout)

    def switch_lock(self, enabled):
        self.lock_button.setEnabled(enabled)
        if self.project_control.selected_item.locked:
            self.lock_button.setChecked(True)
        else:
            self.lock_button.setChecked(False)

    def create_project(self):
        '''
        create a new project
        return True if new project was created
        '''
        (project_name, project_folder, ok) = NewProjectDialog.getValues()
        if ok:
            do_continue = True
            #save already opened project before changing?
            if self.project_has_changed:
                do_continue = self.project_changed_message()
            if do_continue:
                self.project_control.new_project(project_name, project_folder)
                self.project_has_changed = False
                project_file = self.project_control.project.filename
                self.save_project(os.path.join(project_file))
                config.add_to_history(project_folder)
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
        #current = config.settings['environment']['default_project_folder']
        h = config.settings['history']
        if len(h) > 0:
            recent = h[0]
        else:
            recent = '.'
        project_folder = str(QtGui.QFileDialog.getExistingDirectory(
            self, _fromUtf8('Projektordner auswählen'),  recent))
        if len(project_folder) > 0:
            project_file = os.path.join(project_folder, Project.FILENAME_DEFAULT)
            if os.path.isfile(project_file):
                do_continue = True
                if self.project_has_changed:
                    do_continue = self.project_changed_message()
                if do_continue:
                    self.project_control.read_project(project_file)
                    config.add_to_history(project_folder)
                    self.project_has_changed = False
                    return True
            else:
                QtGui.QMessageBox.about(
                    self,
                    _fromUtf8('Ungültiger Projektordner'),
                    "Im angegebenen Ordner konnte keine " +
                    Project.FILENAME_DEFAULT + " gefunden werden!")
        return False

    def save_project(self, filename=None):
        '''
        save the project
        return True if project was saved
        '''
        if not filename:
            dialog_opened = True
            filename = str(QtGui.QFileDialog.getSaveFileName(
                self, 'Projekt speichern', '.', '*.xml'))
        else:
            dialog_opened = False
        #filename is '' if aborted (file dialog returns no status)
        if len(filename) > 0:
            self.project_control.write_project(filename)
            self.project_has_changed = False
        if dialog_opened:
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
        self.save_project(os.path.join(self.project_control.project.filename))
        self.project_control.validate_project()
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
        self.save_project(os.path.join(self.project_control.project.filename))



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

