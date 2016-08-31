# -*- coding: utf-8 -*-
from gui_vm.view.progress_ui import Ui_ProgressDialog
from gui_vm.view.new_project_ui import Ui_NewProject
from gui_vm.view.new_scenario_ui import Ui_NewScenario
from gui_vm.view.settings_ui import Ui_Settings
from gui_vm.model.backend import hard_copy, get_free_space
from gui_vm.model.project_tree import Project
from gui_vm.model.traffic_model import TrafficModel
from PyQt4 import QtGui, QtCore
import sys, os, collections
import re
from gui_vm.config.config import Config
from shutil import rmtree
import datetime

config = Config()

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

XML_FILTER = 'XML-Dateien (*.xml)'
ALL_FILES_FILTER = 'Alle Dateien (*.*)'
HDF5_FILES_FILTER = 'HDF5-Dateien (*.h5)'
CALLABLE_FILES_FILTER = 'Ausführbare Dateien (*.exe)'
PROJECT_FILE_FILTER = 'Projektdatei ({})'.format(Project.FILENAME_DEFAULT)
TRAFFICMODEL_FILE_FILTER = 'Verkehrsmodell ({})'.format(Project.FILENAME_DEFAULT)

DEFAULT_STYLE = """
QProgressBar{
    border: 2px solid grey;
    border-radius: 5px;
    text-align: center
}

QProgressBar::chunk {
    background-color: lightblue;
    width: 10px;
    margin: 1px;
}
"""

ABORTED_STYLE = """
QProgressBar{
    border: 2px solid grey;
    border-radius: 5px;
    text-align: center
}

QProgressBar::chunk {
    background-color: red;
    width: 10px;
    margin: 1px;
}
"""

def remove_special_chars(text):
    '''
    removes Umlaute etc., keeps middle spaces, removes leading and trailing spaces
    '''
    return re.sub('[^A-Za-z0-9 ]+', '', text).strip()

def browse_file(parent, directory=None, filters=None, selected_filter_idx=None):
    if not filters:
        filters=[ALL_FILES_FILTER]
    if not selected_filter_idx:
        selected_filter_idx = 0
    filename = str(
        QtGui.QFileDialog.getOpenFileName(
            parent, _fromUtf8('Datei wählen'),
            directory,
            _fromUtf8(';;'.join(filters)),
            _fromUtf8(filters[selected_filter_idx])
        ))
    return filename

def set_file(parent, line_edit, directory=None, filters=None, selected_filter_idx=None, do_split=False):
    '''
    open a file browser to put a path to a file into the given line edit
    '''
    # set directory to directory of current entry if not given
    if not directory:
        try:
            directory = os.path.split(str(line_edit.text()))[0]
        except:
            directory = ''

    filename = browse_file(parent, directory=directory, filters=filters,
                          selected_filter_idx=selected_filter_idx)

    if do_split:
        filename = os.path.split(filename)[0]

    # filename is '' if canceled
    if len(filename) > 0:
        line_edit.setText(filename)

def set_directory(parent, line_edit):
    dirname = str(
            QtGui.QFileDialog.getExistingDirectory(
                parent, _fromUtf8('Zielverzeichnis wählen')))
    # dirname is '' if canceled
    if len(dirname) > 0:
        line_edit.setText(dirname)

class CopyFilesDialog(QtGui.QDialog, Ui_ProgressDialog):
    '''
    Parameter
    ---------
    filenames: list of Strings,
           filenames of the files to be copied
    destinations: list of Strings,
                  folders where the files shall be copied
    '''

    def __init__(self, filenames, destinations, parent=None):
        super(CopyFilesDialog, self).__init__(parent=None)
        self.parent = parent
        self.setupUi(self)
        #self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.startButton.hide()
        self.cancelButton.clicked.connect(self.close)
        self.cancelButton.setText('OK')
        self.cancelButton.setDisabled(True)
        self.show()
        self.copy(filenames, destinations)
        self.cancelButton.setDisabled(False)

    def copy(self, filenames, destinations):

        #todo: store changed filenames in this dict
        self.changed_filenames = {}

        if not hasattr(filenames, '__iter__'):
            filenames = [filenames]
        if not hasattr(destinations, '__iter__'):
            destinations = [destinations]
        yes_to_all = False

        #check if sum of filesizes exceed free disk space
        #(assuming all files are copied to the same drive)
        size = 0
        for filename in filenames:
            if os.path.exists(filename):
                statinfo = os.stat(filename)
                size += statinfo.st_size
        drive = os.path.splitdrive(destinations[0])[0]
        not_enough = False
        # don't know how to get the root drive under linux, splitdrive returns ''
        # ignored by now, only windows checked
        if drive != '':
            free = get_free_space(drive)
            not_enough = size >= free
        if not_enough:
            status_txt = _fromUtf8("Nicht genug Platz auf {} vorhanden!\n".format(
                destinations[0]) + "Es werden {} kB benötigt".format(
                size/1024) + " aber nur {} kB sind frei".format(
                free/1024))
            QtGui.QMessageBox.about(None, "Fehler", status_txt)
            self.close()

        else:
            for i in xrange(len(filenames)):
                if not os.path.exists(filenames[i]):
                    status_txt = '<i><b>{}</b> existiert nicht ... &uuml;berspringe </i><br>'.format(filename)
                    self.log_edit.insertHtml(status_txt)
                    continue

                d, filename = os.path.split(filenames[i])
                dest_filename = os.path.join(destinations[i], filename)
                do_copy = True
                if os.path.exists(dest_filename) and not yes_to_all:
                    msgBox = QtGui.QMessageBox()
                    msgBox.setText(_fromUtf8("Die Datei {} existiert bereits."
                                    .format(filename) +
                                    "\nWollen Sie sie überschreiben?"))
                    msgBox.addButton(QtGui.QPushButton('Ja'),
                                     QtGui.QMessageBox.YesRole)
                    yta_btn = QtGui.QPushButton(_fromUtf8('Ja für Alle'))
                    msgBox.addButton(yta_btn, QtGui.QMessageBox.YesRole)
                    if len(filenames) == 1:
                        yta_btn.setDisabled(True)
                    msgBox.addButton(QtGui.QPushButton('Nein'),
                                     QtGui.QMessageBox.NoRole)
                    msgBox.addButton(QtGui.QPushButton('Abbrechen'),
                                     QtGui.QMessageBox.RejectRole)
                    reply = msgBox.exec_()
                    do_copy = reply == 0
                    yes_to_all = reply == 1
                    no = reply == 2
                    cancel = reply == 3
                    if cancel:
                        return
                if do_copy or yes_to_all:
                    status_txt = 'Kopiere <b>{}</b> nach <b>{}</b> ...<br>'.format(
                        filename, destinations[i])
                    self.log_edit.insertHtml(status_txt)
                    success, msg = hard_copy(filenames[i], dest_filename,
                                             callback=self.progress_bar.setValue)
                    if success:
                        status_txt = '{} erfolgreich kopiert<br>'.format(filename)
                    else:
                        status_txt = ('<b>Fehler</b> beim Kopieren von {}<br>'
                                      .format(filename) +
                                      ': ' + msg)
                    self.log_edit.insertHtml(status_txt)
                else:
                    status_txt = '<b>{}</b> nicht kopiert<br>'.format(
                        filename, destinations[i])
                    self.log_edit.insertHtml(status_txt)
                self.log_edit.moveCursor(QtGui.QTextCursor.End)
            self.progress_bar.setValue(100)


class ExecDialog(QtGui.QDialog, Ui_ProgressDialog):

    def __init__(self, scenario, run_name, options=None, parent=None):
        super(ExecDialog, self).__init__(parent=parent)
        self.parent = parent
        self.run_name = run_name
        self.scenario = scenario
        self.options = options
        self.setupUi(self)
        self.setWindowTitle(self.windowTitle() + ' ' + scenario.name + ' / ' + run_name)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.cancelButton.clicked.connect(self.close)
        self.startButton.clicked.connect(self.run)

        # QProcess object for external app
        self.process = QtCore.QProcess(self)

        # Just to prevent accidentally running multiple times
        # Disable the button when process starts, and enable it when it finishes
        self.process.started.connect(self.running)
        self.process.finished.connect(self.finished)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_timer)

        self.show()
        #start process when window is opened
        self.startButton.clicked.emit(True)

    def run(self):
        cancel = False
        primary = self.scenario.primary_run
        # specific runs become invalid if primary run is executed again, delete them
        if primary and primary.is_valid and self.run_name == primary.name:
            if not config.batch_mode:
                dialog = QtGui.QMessageBox()
                msg = 'Das Szenario {} '.format(self.scenario.name) + \
                    'wurde bereits berechnet. \n\n' + \
                    'Wollen Sie trotzdem einen erneuten Gesamtlauf starten?\n\n' + \
                    'Achtung! Die Ergebnisse der spezifischen Läufe des Szenarios werden ebenfalls gelöscht!'
                reply = dialog.question(
                    self, _fromUtf8("erneuter Gesamtlauf"), _fromUtf8(msg),
                    QtGui.QMessageBox.Ok, QtGui.QMessageBox.Cancel)
                cancel = reply == QtGui.QMessageBox.Cancel
            if cancel:
                self.close()
                return
            for output in self.scenario.get_output_files():
                try:
                    rmtree(os.path.split(output.file_absolute)[0])
                except:
                    pass
                pass

        self.start_time = datetime.datetime.now()
        self.timer.start(1000)
        self.scenario.run(self.process, self.run_name, options=self.options,
                          callback=self.show_status)

    def running(self):
        self.progress_bar.setStyleSheet(DEFAULT_STYLE)
        self.progress_bar.setValue(0)
        self.startButton.setEnabled(False)
        self.cancelButton.setText('Stoppen')
        self.cancelButton.clicked.disconnect(self.close)
        self.cancelButton.clicked.connect(self.kill)

    def stopped(self):
        self.timer.stop()
        self.startButton.setEnabled(True)
        self.cancelButton.setText(_fromUtf8('Schließen'))
        self.cancelButton.clicked.disconnect(self.kill)
        self.cancelButton.clicked.connect(self.close)
        if config.batch_mode:
            self.close()

    def finished(self):
        # strange: process returns 1 even if successful
        #if not self.process.Crashed:
        self.progress_bar.setValue(100)
        self.scenario.project.emit()
        self.stopped()

    def kill(self):
        self.timer.stop()
        self.progress_bar.setStyleSheet(ABORTED_STYLE)
        self.process.kill()
        demand_file = self.scenario.get_output(self.run_name).file_absolute
        # tdmks writes during calculations, when aborted file is useless
        if os.path.exists(demand_file):
            os.remove(demand_file)

    def show_status(self, text, progress=None):
        self.log_edit.insertHtml(str(text) + '<br>')
        self.log_edit.moveCursor(QtGui.QTextCursor.End)
        if progress:
            self.progress_bar.setValue(progress)

    def update_timer(self):
        delta = datetime.datetime.now() - self.start_time
        h, remainder = divmod(delta.seconds, 3600)
        m, s = divmod(remainder, 60)
        timer_text = '{:02d}:{:02d}:{:02d}'.format(h, m, s)
        self.elapsed_time_label.setText(timer_text)


class NewProjectDialog(QtGui.QDialog, Ui_NewProject):
    '''
    open a dialog to set the project name and folder and afterwards create
    a new project
    '''

    def __init__(self):
        super(NewProjectDialog, self).__init__()
        self.setupUi(self)
        h = config.settings['history']
        recent = ''
        if len(h) > 0:
            recent = h[0]
        #default = config.settings['environment']['default_project_folder']
        self.folder_edit.setText(recent)
        self.folder_browse_button.clicked.connect(lambda: set_directory(self, self.folder_edit))
        self.show()

    @staticmethod
    def getValues():
        dialog = NewProjectDialog()
        ret = None
        # dialog shall be opened again, if input is not valid
        # true loop will only be exited, if (ok and valid) or canceled
        while True:
            ret = dialog.exec_()
            project_name = str(remove_special_chars(str(dialog.project_edit.text().toAscii())))
            project_folder = str(dialog.folder_edit.text())
            if ret == QtGui.QDialog.Accepted:
                if os.path.exists(project_folder):
                    return (project_name, project_folder, True)
                #ok clicked and not valid -> loop again
                else:
                    QtGui.QMessageBox.about(
                        dialog, "Warnung!", "Verzeichnis {} existiert nicht!"
                        .format(project_folder))
            else:
                return (project_name, project_folder, False)

class RunOptionsDialog(QtGui.QDialog):
    '''
    open a dialog to define the parameters for a special run
    '''

    def __init__(self, scenario_node, stored_options={},
                 parent=None, is_primary = False, standard_button_texts=None):
        super(RunOptionsDialog, self).__init__(parent=parent)
        self.setupUi()
        self.scenario = scenario_node
        self.option_checks = {}
        self.parent = parent

        def create_tab(opt_name, check_names, check_values,
                       stored_options, unique=False):
            tab = QtGui.QWidget()
            grid_layout = QtGui.QGridLayout(tab)
            scroll_area = QtGui.QScrollArea(tab)
            scroll_area.setWidgetResizable(True)
            grid_layout.addWidget(scroll_area, 0, 0, 1, 1)
            self.tabWidget.addTab(tab, _fromUtf8(opt_name))

            widget = QtGui.QWidget()
            layout = QtGui.QVBoxLayout()
            checks = []
            grouped = QtGui.QButtonGroup(widget)

            if not unique:
                grouped.setExclusive(False)
            else:
                grouped.setExclusive(True)

            for i, name in enumerate(check_names):
                checkbox = QtGui.QCheckBox(_fromUtf8(name))

                #check the boxes which are stored in options
                if stored_options and stored_options.has_key(opt_name)\
                   and str(check_values[i]) in str(stored_options[opt_name]).strip():
                    checkbox.setChecked(True)
                grouped.addButton(checkbox)
                layout.addWidget(checkbox)
                checks.append(checkbox)

            layout.addSpacerItem(QtGui.QSpacerItem(20,40,
                    QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding))
            widget.setLayout(layout)
            scroll_area.setWidget(widget)
            return dict(zip(check_values, checks))

        model_options = self.scenario.model.options
        for option, attr in model_options.items():
            if (attr.has_key('default') and not stored_options.has_key(option)):
                index = int(attr['default'])
                stored_options[option] = [attr['values'][index]]
            unique = attr.has_key('is_unique') and bool(attr['is_unique'])
            tagged_as_primary_only = attr.has_key('is_primary_only') and bool(attr['is_primary_only'])
            tagged_as_special_only = attr.has_key('is_special_only') and bool(attr['is_special_only'])
            if ((not is_primary and not tagged_as_primary_only) or
                (is_primary and not tagged_as_special_only)):
                self.option_checks[option] = create_tab(
                    option, attr['names'], attr['values'], stored_options, unique)
        self.show()

    def setupUi(self):
        self.setObjectName(_fromUtf8("RunOptions"))
        self.resize(372, 362)
        self.setModal(True)
        self.gridLayout = QtGui.QGridLayout(self)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        buttonBox = QtGui.QDialogButtonBox(self)
        buttonBox.setOrientation(QtCore.Qt.Horizontal)
        buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        # buttonBox.button(QtGui.QDialogButtonBox.Ok).setText(standard_button_texts[0])
        # buttonBox.button(QtGui.QDialogButtonBox.Cancel).setText(standard_button_texts[1]) _fromUtf8('Änderungen speichern')
        self.horizontalLayout.addWidget(buttonBox)
        QtCore.QObject.connect(buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), self.accept)
        QtCore.QObject.connect(buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), self.reject)

        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 1)
        self.tabWidget = QtGui.QTabWidget(self)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)

        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(self)

    @staticmethod
    def getValues(scenario_node, stored_options={}, is_primary = False):
        
        model_options = scenario_node.model.options
        # no options -> no need to configure anything
        if len(model_options) == 0:
            return None, True
        dialog = RunOptionsDialog(
            scenario_node, stored_options=stored_options,
            is_primary=is_primary)
        run_type = 'Gesamtlauf' if is_primary else 'spezifischen Lauf'
        title = _fromUtf8('Optionen für {} in "{}"'.format(run_type, scenario_node.name))
        dialog.setWindowTitle(title)
        ok = dialog.exec_()
        accepted = ok == QtGui.QDialog.Accepted
        checks = dialog.option_checks
        if ok:
            for opt_name, opt in checks.items():
                opt_arr = []
                for k, v in opt.items():
                    if v.isChecked():
                        opt_arr.append(str(k))
                if len(opt_arr) > 0:
                    checks[opt_name] = opt_arr
                else:
                    checks.pop(opt_name)
            return checks, ok
        return None, False


class InputDialog(QtGui.QDialog):
    '''
    open a dialog to set the project name and folder and afterwards create
    a new project
    '''

    def __init__(self, title, default):
        super(InputDialog, self).__init__()
        self.setWindowTitle(title)
        self.resize(409, 159)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setMinimumSize(QtCore.QSize(409, 159))
        self.setMaximumSize(QtCore.QSize(409, 159))
        self.setSizeGripEnabled(False)
        self.setModal(True)
        gridLayout = QtGui.QVBoxLayout(self)
        buttonBox = QtGui.QDialogButtonBox(self)
        self.edit = QtGui.QLineEdit(self)
        self.edit.setText(_fromUtf8(default))
        gridLayout.addWidget(self.edit)
        buttonBox.setOrientation(QtCore.Qt.Horizontal)
        buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        gridLayout.addWidget(buttonBox)

        QtCore.QObject.connect(buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), self.accept)
        QtCore.QObject.connect(buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), self.reject)

    @staticmethod
    def getValues(title, default):
        dialog = InputDialog(title, default)
        ok = dialog.exec_()
        accepted = ok == QtGui.QDialog.Accepted
        text = str(remove_special_chars(str(dialog.edit.text().toAscii())))
        return text, accepted

class NewScenarioDialog(QtGui.QDialog, Ui_NewScenario):
    '''
    open a dialog to set the scenario name and traffic model to work with
    '''

    def __init__(self, default_name):
        super(NewScenarioDialog, self).__init__()
        self.setupUi(self)
        self.name_edit.setText(default_name)
        self.combo_model.addItems(config.settings['trafficmodels'].keys())
        self.show()

    @staticmethod
    def getValues(default_name=''):
        dialog = NewScenarioDialog(default_name)
        ok = dialog.exec_()
        simrun_name = str(remove_special_chars(str(dialog.name_edit.text().toAscii())))
        model_name = str(dialog.combo_model.currentText())
        accepted = ok == QtGui.QDialog.Accepted
        return (simrun_name, model_name, accepted)


class SettingsDialog(QtGui.QDialog, Ui_Settings):
    '''
    open a dialog to set the project name and folder and afterwards create
    a new project
    '''

    def __init__(self, parent=None):
        super(SettingsDialog, self).__init__(parent)
        self.setupUi(self)
        self.restart_required = False
        
        self.models_ui_elements = {}
        self.hdf5_exec_browse_button.clicked.connect(
            lambda: set_file(self, self.hdf5_edit,
                             filters=[ALL_FILES_FILTER, CALLABLE_FILES_FILTER],
                             selected_filter_idx=1)
        )
        
        self.models_layout = QtGui.QVBoxLayout(self.models_scroll_content)
        models = config.settings['trafficmodels']
        for name in models:
            self.add_model_content(name)
            
        spacer = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.models_layout.addItem(spacer)

        #def enable_restart_required():
            #self.restart_required = True

        #self.auto_check.stateChanged.connect(enable_restart_required)

        #self.verkmod_default_browse_button.setDisabled(True)
        #self.verkmod_exec_browse_button.setDisabled(True)

        self.OK_button.clicked.connect(self.write_config)
        self.reset_button.clicked.connect(self.reset)
        self.cancel_button.clicked.connect(self.close)
        self.fill()
        self.show()
        
    def add_model_content(self, name):
        self.models_ui_elements[name] = {}
        elements = self.models_ui_elements[name]
        
        box = QtGui.QGroupBox(self.models_scroll_content)
        box.setTitle(name)
        vertical_layout = QtGui.QVBoxLayout(box)
        grid_layout = QtGui.QGridLayout()
        
        # default folder
        label = QtGui.QLabel(box)
        label.setText('Defaultordner')        
        grid_layout.addWidget(label, 0, 0, 1, 1)
        default_edit = QtGui.QLineEdit(box)        
        grid_layout.addWidget(default_edit, 0, 1, 1, 1)
        default_browse_button = QtGui.QPushButton(box)
        default_browse_button.setText('...')
        default_browse_button.setMaximumSize(QtCore.QSize(30, 16777215))
        grid_layout.addWidget(default_browse_button, 0, 3, 1, 1)
        
        # executable
        label = QtGui.QLabel(box)
        label.setText('Programmdatei')        
        grid_layout.addWidget(label, 1, 0, 1, 1)
        exec_edit = QtGui.QLineEdit(box)
        grid_layout.addWidget(exec_edit, 1, 1, 1, 1)        
        exec_browse_button = QtGui.QPushButton(box)
        exec_browse_button.setMaximumSize(QtCore.QSize(30, 16777215))
        exec_browse_button.setText('...')
        grid_layout.addWidget(exec_browse_button, 1, 3, 1, 1)
        
        # arguments
        label = QtGui.QLabel(box)
        label.setText('Argumente')    
        arguments_edit = QtGui.QLineEdit(box)
        grid_layout.addWidget(label, 2, 0, 1, 1)        
        grid_layout.addWidget(arguments_edit, 2, 1, 1, 1)
        
        vertical_layout.addLayout(grid_layout)
        self.models_layout.addWidget(box)  
        
        
        default_browse_button.clicked.connect(
            lambda: set_file(self, default_edit,
                             filters=[ALL_FILES_FILTER, TRAFFICMODEL_FILE_FILTER],
                             selected_filter_idx=1,
                             do_split=True)
        )
        exec_browse_button.clicked.connect(
            lambda: set_file(self, exec_edit,
                             filters=[ALL_FILES_FILTER, CALLABLE_FILES_FILTER],
                             selected_filter_idx=1)
        )        
        
        elements['exec'] = exec_edit    
        elements['default'] = default_edit   
        elements['args'] = arguments_edit   

    def fill(self):
        env = config.settings['environment']

        self.hdf5_edit.setText(env['hdf5_viewer'])

        # add traffic models
        models = config.settings['trafficmodels']
        self.auto_check.setChecked(config.settings['auto_check'])
        
        for name, values in models.iteritems():
            ui_elements = self.models_ui_elements[name]
            ui_elements['default'].setText(values['default_folder'])
            ui_elements['exec'].setText(values['executable'])
            ui_elements['args'].setText(values['arguments'])

    def write_config(self):
        env = config.settings['environment']
        #env['default_project_folder'] = str(self.project_edit.text())
        env['hdf5_viewer'] = str(self.hdf5_edit.text())

        models = config.settings['trafficmodels']
        for name, values in models.iteritems():
            ui_elements = self.models_ui_elements[name]
            values['default_folder'] = str(ui_elements['default'].text())
            values['executable'] = str(ui_elements['exec'].text())
            values['arguments'] = str(ui_elements['args'].text())

        config.settings['auto_check'] = self.auto_check.isChecked()

        config.write()
        if self.restart_required:
            QtGui.QMessageBox.information(None, "Neustart erforderlich", u"Die geänderte Einstellung wird erst wirksam nach einem Neustart der Oberfläche")
        self.close()

    def reset(self):
        config.reset()


class CopySpecialRunDialog(QtGui.QDialog):
    '''
    open a dialog to set the project name and folder and afterwards create
    a new project
    '''

    def __init__(self, output_node):
        super(CopySpecialRunDialog, self).__init__()
        self.setWindowTitle("{} kopieren".format(output_node.name))
        self.resize(409, 159)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setMinimumSize(QtCore.QSize(409, 159))
        self.setMaximumSize(QtCore.QSize(409, 159))
        self.setSizeGripEnabled(False)
        self.setModal(True)

        self.gridLayout = QtGui.QGridLayout(self)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.name_edit = QtGui.QLineEdit(self)
        self.name_edit.setText("{}".format(output_node.name))
        self.gridLayout.addWidget(self.name_edit, 1, 1, 1, 1)
        self.name_label = QtGui.QLabel(self)
        self.name_label.setText("Neuer Name")
        self.gridLayout.addWidget(self.name_label, 1, 0, 1, 1)

        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.gridLayout.addWidget(self.buttonBox, 6, 0, 1, 2)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), self.reject)

        self.combo_model = QtGui.QComboBox(self)
        self.gridLayout.addWidget(self.combo_model, 2, 1, 1, 1)
        self.combo_label = QtGui.QLabel(self)
        self.combo_label.setText("Ziel-Szenario")
        self.gridLayout.addWidget(self.combo_label, 2, 0, 1, 1)

        scenario_names = []
        idx = 0
        for i, scen in enumerate(output_node.scenario.project.get_children()):
            scenario_names.append(scen.name)
            if scen == output_node.scenario:
                idx = i
        self.combo_model.addItems(scenario_names)
        self.combo_model.setCurrentIndex(idx)

        self.show()

    @staticmethod
    def getValues(output_node):
        dialog = CopySpecialRunDialog(output_node)
        ret = None
        project = output_node.scenario.project
        # dialog shall be opened again, if input is not valid
        # true loop will only be exited, if (ok and valid) or canceled
        while True:
            ret = dialog.exec_()
            output_name = str(remove_special_chars(str(dialog.name_edit.text().toAscii())))
            scenario_name = str(dialog.combo_model.currentText())
            if ret == QtGui.QDialog.Accepted:
                success = True
                dest_scen = project.get_child(scenario_name)
                if len(dest_scen.find_all(output_name)) > 0:
                    QtGui.QMessageBox.about(
                        dialog,  "Warnung!",
                        _fromUtf8('"{}" enthält bereits einen Lauf mit dem Namen "{}"!'
                        .format(scenario_name, output_name)))
                    continue

                #check if options and values are same in both scenarios
                #(otherwise no sense in copying runs between scenarios)
                origin_scen = output_node.scenario
                if origin_scen.name != scenario_name:
                    compare = lambda a, b: collections.Counter(a) == collections.Counter(b)
                    for option, values in dest_scen.model.options.items():
                        if not compare(values['values'], origin_scen.model.options[option]['values']):
                            QtGui.QMessageBox.about(
                                dialog,  "Warnung!",
                                _fromUtf8('Ausgangs-Szenario "{}" und Ziel-Szenario "{}" haben verschiedene Eingangs-Parameter!'
                                .format(origin_scen.name, scenario_name)))
                            success = False
                            break
                if success:
                    return (output_name, scenario_name, True)
            else:
                return (None, None, False)