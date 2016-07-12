# -*- coding: utf-8 -*-
import sys, os
from functools import partial
from gui_vm.view.main_window_ui import Ui_MainWindow
from gui_vm.view.welcome_ui import Ui_Welcome
from PyQt4 import QtGui, QtCore
from gui_vm.control.project_control import VMProjectControl
from gui_vm.control.project_control import disable_while_processing
from gui_vm.model.project_tree import Project
from gui_vm.control.dialogs import (NewProjectDialog, SettingsDialog,
                                    browse_file, PROJECT_FILE_FILTER)
from gui_vm.config.config import Config
from gui_vm.model.project_tree import TreeNode, Scenario

config = Config()

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s


class MainWindow(QtGui.QMainWindow, Ui_MainWindow):

    @classmethod
    def only_validate(cls, project_file, scenario_name):
        """
        only
        """
        self = MainWindow(project_file, scenario_name)
        self.scenario_choice_button.setVisible(True)
        scenario_node = self.project_control.project.get_child(scenario_name)
        if scenario_node:
            if scenario_node.is_valid:
                # everything is ok
                self.project_control.close_project()
                self.validated = True
        return self

    def __init__(self,
                 project_file=None,
                 run_scenario=None,
                 admin_mode=False,
                 save_disabled=False):
        """
        """
        QtGui.QMainWindow.__init__(self)
        self.setupUi(self)

        # global access to main window
        config.mainWindow = self
        # global access to admin mode
        config.admin_mode = admin_mode

        config.save_disabled = save_disabled

        # define the view on the project and connect to the qtreeview in
        # the main window
        self.project_tree = TreeNode('root')
        self.project_control = VMProjectControl(
            view=self.qtreeview, button_group=self.context_button_group,
            details_view=self.details_layout)
        self.qtreeview.setModel(self.project_control)
        self.qtreeview.clicked[QtCore.QModelIndex].connect(
            self.project_control.select_item)

        self.qtreeview.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.qtreeview.customContextMenuRequested.connect(
            self.project_control.pop_context_menu)

        self.project_has_changed = False
        self.recently_used_actions = []

        self.open_button.clicked.connect(
            lambda: disable_while_processing(self.load_project))
        self.new_button.clicked.connect(
            lambda: disable_while_processing(self.create_project))

        # connect the menubar
        self.actionProjekt_ffnen.triggered.connect(
            lambda: disable_while_processing(self.load_project))
        self.actionNeues_Szenario.triggered.connect(
            lambda: disable_while_processing(self.project_control.add_scenario))
        self.actionNeues_Projekt.triggered.connect(
            lambda: disable_while_processing(self.create_project))
        self.actionEinstellungen.triggered.connect(
            lambda: disable_while_processing(self.edit_settings))
        self.actionInfo.triggered.connect(
            lambda: disable_while_processing(self.show_info))
        self.actionProjekt_schlie_en.triggered.connect(
            lambda: disable_while_processing(self.project_control.close_project))

        self.actionSzenario_duplizieren.triggered.connect(
            lambda: self.project_control.clone_scenario(do_choose=True))
        self.actionSzenario_l_schen.triggered.connect(
            lambda: self.project_control.remove_scenario(do_choose=True))

        self.actionGesamtlauf_starten.triggered.connect(
            lambda: self.project_control.run(do_choose=True, run_name=Scenario.PRIMARY_RUN))
        self.actionSpezifischen_Lauf_anlegen.triggered.connect(
            lambda: self.project_control.add_special_run(do_choose=True))

        self.scenario_choice_button.clicked.connect(self.close)
        self.scenario_choice_button.setVisible(False)

        self.actionBeenden.triggered.connect(self.close)

        self.project_control.project_changed.connect(self.project_changed_handler)

        h = config.settings['history']
        self.validated = False

        # if project is passed, open it
        if project_file:
            self.load_project(project_file)

        # no project passed in arguments -> open recent project from history
        elif len(h) > 0:
            project_file = os.path.join(h[0], Project.FILENAME_DEFAULT)
            self.load_project(project_file)
        #welcome screen if there is none (assumed first start)
        else:
            welcome = WelcomeDialog(self)

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
            'Copyright: Gertz Gutsche Rümenapp, 2015\n'))

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
            project_file = browse_file(self, directory=recent,
                                       filters=[PROJECT_FILE_FILTER])
        project_folder = os.path.split(project_file)[0]
        if len(project_file) > 0:
            if os.path.isfile(project_file):
                do_continue = True
                if self.project_has_changed:
                    do_continue = self.project_changed_message()
                if do_continue:
                    self.project_control.read_project(project_file)
                    config.add_to_history(os.path.split(project_file)[0])
                    self.project_has_changed = False
                    self.build_history()
                    return True
            else:
                config.remove_from_history(os.path.split(project_file)[0])
                QtGui.QMessageBox.about(
                    self,
                    _fromUtf8('Ungültiger Projektpfad'),
                    'Die Projektdatei "{}" exisitiert nicht.'.format(project_file))
                self.build_history()
                return False
        return False

    def save_project(self, filename=None):
        '''
        save the project
        return True if project was saved
        '''
        if config.save_disabled:
            return
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
        # TODO: autosave option (currently true)
        self.save_project(os.path.join(self.project_control.project.filename))

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

    def batch_clone_scenario(self, source_scenario_name, new_scenario_name):
        config.batch_mode = True
        project = self.project_control.project
        source_scenario = project.get_child(source_scenario_name)
        if not source_scenario:
            QtGui.QMessageBox.about(
                None, "Fehler",
                _fromUtf8("Das Szenario '{}' existiert nicht."
                          .format(source_scenario_name)))
            return
        self.project_control.clone_scenario(scenario_node=source_scenario,
                                            new_scenario_name=new_scenario_name)

    # to be called when command line arguments are passed
    def batch_run(self, scenario_name, run_name=Scenario.PRIMARY_RUN, do_calibrate=False, do_balancing=True):
        config.batch_mode = True
        scenario_node = self.project_control.project.get_child(scenario_name)
        if not scenario_node:
            QtGui.QMessageBox.about(
                None, 'Fehler',
                'Szenario "{}" nicht gefunden!'.format(scenario_name))
            return
        if scenario_node.locked:
            QtGui.QMessageBox.about(
                None, 'Fehler',
                'Szenario "{}" ist gesperrt!'.format(scenario_name))
            return
        options = {}
        if run_name == Scenario.PRIMARY_RUN:
            options = {'calibrate': [str(do_calibrate)], 'balance': [str(do_balancing)]}
        else:
            specific_run = scenario_node.get_output(run_name)
            if not specific_run:
                QtGui.QMessageBox.about(
                    None, 'Fehler',
                    'Lauf "{}" in Szenario "{}" nicht gefunden!'.format(run_name, scenario_name))
                return
            options = specific_run.options
        self.project_control.run(scenario_node, run_name=run_name, options=options)


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

