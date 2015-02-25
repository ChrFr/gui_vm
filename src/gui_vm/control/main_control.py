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

    def __init__(self, project_file=None, run_scenario=None):
        QtGui.QMainWindow.__init__(self)
        self.setupUi(self)
        # define the view on the project and connect to the qtreeview in
        # the main window
        self.project_tree = TreeNode('root')
        self.project_control = VMProjectControl(
            view=self.qtreeview, button_group=self.context_button_group,
            details_view=self.details_layout)
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

        # connect the menubar
        self.actionNeues_Szenario.triggered.connect(
            self.project_control.add_scenario)
        self.actionNeues_Projekt.triggered.connect(self.create_project)
        self.actionEinstellungen.triggered.connect(self.edit_settings)
        self.actionInfo.triggered.connect(self.show_info)
        self.actionProjekt_schlie_en.triggered.connect(self.project_control.close_project)
        self.actionSzenario_duplizieren.triggered.connect(
            lambda: self.project_control.clone_scenario(do_choose=True))
        self.actionSzenario_l_schen.triggered.connect(
            lambda: self.project_control.remove_scenario(do_choose=True))
        self.actionBeenden.triggered.connect(QtGui.qApp.quit)

        self.project_control.project_changed.connect(self.project_changed_handler)
        self.project_changed.connect(self.project_changed_handler)

        h = config.settings['history']

        # if project is passed, open it
        if project_file:
            if os.path.isfile(project_file):
                self.project_control.read_project(project_file)
            else:
                QtGui.QMessageBox.about(
                    self, 'Fehler', 'Projektdatei {} nicht gefunden'.
                    format(project_file))
        elif len(h) > 0:
            self.build_history()

            #open recent project
            project_file = os.path.join(h[0], Project.FILENAME_DEFAULT)
            if os.path.isfile(project_file):
                self.project_control.read_project(project_file)
        #welcome screen if there is none (assumed first start)
        else:
            welcome = WelcomeDialog(self)

        if run_scenario:
            self.project_control.run(run_scenario)

    def build_history(self):
        self.recently_used_actions = []
        self.menuZuletzt_benutzt.clear()
        for recent in config.settings['history']:
            #build history menu and connect it to open the recent projects
            action = QtGui.QAction(self)
            action.setText(_fromUtf8(recent))
            self.recently_used_actions.append(action)
            self.menuZuletzt_benutzt.addAction(action)
            project_file = os.path.join(recent, Project.FILENAME_DEFAULT)
            action.triggered.connect(partial((
                lambda filename: self.load_project(filename)),
                                             project_file))

    def show_info(self):
        QtGui.QMessageBox.about(
            self, 'Info', _fromUtf8('Oberfläche für Verkehrsmodelle. \n' +
            'Copyright: Gertz Gutsche Rümenapp, 2015\n' +
            'Version: 0.5'))

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
                ok = self.project_control.new_project(project_name, project_folder)
                if not ok:
                    return False
                self.project_has_changed = False
                project_file = self.project_control.project.filename
                self.save_project(os.path.join(project_file))
                config.add_to_history(project_folder)
                self.build_history()
                return True
        else:
            return False

    def edit_settings(self):
        SettingsDialog(self)

    def load_project(self, project_file=None):
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
        if not project_file:
            project_file = str(QtGui.QFileDialog.getOpenFileName(
                self, _fromUtf8('Projektdatei auswählen'),  recent, Project.FILENAME_DEFAULT))
        project_folder = os.path.split(project_file)[0]
        if len(project_file) > 0:
            if os.path.isfile(project_file):
                do_continue = True
                if self.project_has_changed:
                    do_continue = self.project_changed_message()
                if do_continue:
                    self.project_control.read_project(project_file)
                    config.add_to_history(os.path.split(project_file)[0])
                    self.build_history()
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
        project = self.project_control.project
        if project is not None:
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

