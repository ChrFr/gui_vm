# -*- coding: utf-8 -*-
from gui_vm.view.progress_ui import Ui_ProgressDialog
from gui_vm.view.new_project_ui import Ui_NewProject
from gui_vm.view.new_scenario_ui import Ui_NewScenario
from gui_vm.view.settings_ui import Ui_Settings
from gui_vm.model.backend import hard_copy, get_free_space
from PyQt4 import QtGui, QtCore
import sys, os, collections
import re
from gui_vm.config.config import Config
from shutil import rmtree

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
                    if len(filenames) > 1:
                        msgBox.addButton(QtGui.QPushButton(_fromUtf8('Ja für Alle')),
                                         QtGui.QMessageBox.YesRole)
                    msgBox.addButton(QtGui.QPushButton('Nein'),
                                     QtGui.QMessageBox.NoRole)
                    msgBox.addButton(QtGui.QPushButton('Abbrechen'),
                                     QtGui.QMessageBox.RejectRole)
                    reply = msgBox.exec_()
                    do_copy = reply == 0
                    yes_to_all = reply == 1
                    cancel = reply == 3
                    if cancel:
                        #self.cancelButton.setText('OK')
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
                    'Achtung! Die Ergebnisse der spezifischen LÃ¤ufe des Szenarios werden ebenfalls gelÃ¶scht!'
                reply = dialog.question(
                    self, _fromUtf8("erneuter Gesamtlauf"), _fromUtf8(msg),
                    QtGui.QMessageBox.Ok, QtGui.QMessageBox.Cancel)
                cancel = reply == QtGui.QMessageBox.Cancel
            if not cancel:
                for output in self.scenario.get_output_files():
                    try:
                        rmtree(os.path.split(output.file_absolute)[0])
                    except:
                        pass
                    pass

        if not cancel:
            # run the process
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
        self.folder_browse_button.clicked.connect(self.browse_folder)
        self.show()

    def browse_folder(self):
        '''
        open a file browser to set the project folder
        '''
        folder = str(
            QtGui.QFileDialog.getExistingDirectory(
                self, 'Projektverzeichnis wählen', directory=self.folder_edit.text()))
        #filename is '' if canceled
        if len(folder) > 0:
            self.folder_edit.setText(folder)

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
                stored_options[option] = [attr['default']]
            unique = attr.has_key('is_unique') and attr['is_unique'] == True
            if ((not is_primary and not attr['is_primary_only']) or
                (is_primary and not attr['is_special_only'])):
                self.option_checks[option] = create_tab(
                    option, attr['names'], attr['values'], stored_options, unique)
        self.show()

    def setupUi(self):
        self.setObjectName(_fromUtf8("RunOptions"))
        self.resize(372, 362)
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

        self.retranslateUi(self)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self, RunOptions):
        RunOptions.setWindowTitle(_translate("RunOptions", "Optionen", None))

    @staticmethod
    def getValues(scenario_node, stored_options={}, is_primary = False):
        dialog = RunOptionsDialog(
            scenario_node, stored_options=stored_options,
            is_primary=is_primary)
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

        self.python_exec_browse_button.clicked.connect(
            lambda: self.set_file(self.python_edit, 'python.exe'))
        self.hdf5_exec_browse_button.clicked.connect(
            lambda: self.set_file(self.hdf5_edit, '*.exe'))
        self.maxem_default_browse_button.clicked.connect(
            lambda: self.set_file(self.maxem_default_edit, 'project.xml', True))
        self.maxem_exec_browse_button.clicked.connect(
            lambda: self.set_file(self.maxem_exec_edit, '*.py'))
        self.verkmod_default_browse_button.setDisabled(True)
        self.verkmod_exec_browse_button.setDisabled(True)
        #self.verkmod_default_browse_button.clicked.connect(
            #lambda: self.set_folder(self.verkmod_default_edit))
        #self.verkmod_exec_browse_button.clicked.connect(
            #lambda: self.set_file(self.verkmod_exec_edit, '*.exe'))

        self.OK_button.clicked.connect(self.write_config)
        self.reset_button.clicked.connect(self.reset)
        self.cancel_button.clicked.connect(self.close)
        self.auto_python_button.clicked.connect(self.set_python_auto)
        self.fill()
        self.show()

    def set_python_auto(self):
        path = ''

        try:
            #linux
            path = os.path.split(os.environ['PYTHONPATH'])[0]
        except KeyError:
            #Windows
            try:
                f = ''
                for p in os.environ['PATH'].split(';'):
                    if 'python' in p.lower():
                        f = p
                        break
                for s in f.split('\\'):
                    path += s + '\\'
                    if 'python' in s.lower():
                        break
            except KeyError:
                path = ''

        self.python_edit.setText(os.path.join(path, 'python.exe'))

    def fill(self):
        env = config.settings['environment']

        self.hdf5_edit.setText(env['hdf5_viewer'])

        mod = config.settings['trafficmodels']
        maxem = mod['Maxem']
        self.maxem_default_edit.setText(maxem['default_folder'])
        self.maxem_exec_edit.setText(maxem['executable'])
        self.python_edit.setText(maxem['interpreter'])

        #verkmod = mod['VerkMod']
        #self.verkmod_default_edit.setText(verkmod['default_folder'])
        #self.verkmod_exec_edit.setText(verkmod['executable'])


    def set_file(self, line_edit, extension, do_split=False):
        '''
        open a file browser to put a path to a file into the given line edit
        '''
        try:
            current = os.path.split(str(line_edit.text()))[0]
        except:
            current = ''

        filename = str(
            QtGui.QFileDialog.getOpenFileName(
                self, _fromUtf8('Datei wählen'), current+'/'+extension))
        if do_split:
            filename = os.path.split(filename)[0]
        #filename is '' if canceled
        if len(filename) > 0:
            line_edit.setText(filename)

    def set_folder(self, line_edit):
        '''
        open a file browser to put a directory into the given line edit
        '''
        folder = str(
            QtGui.QFileDialog.getExistingDirectory(
                self, 'Ordner wählen', directory=line_edit.text()))
        #folder is '' if canceled
        if len(folder) > 0:
            line_edit.setText(folder)

    def write_config(self):
        env = config.settings['environment']
        #env['default_project_folder'] = str(self.project_edit.text())
        env['hdf5_viewer'] = str(self.hdf5_edit.text())

        mod = config.settings['trafficmodels']
        maxem = mod['Maxem']
        maxem['default_folder'] = str(self.maxem_default_edit.text())
        maxem['executable'] = str(self.maxem_exec_edit.text())
        maxem['interpreter'] = str(self.python_edit.text())

        #verkmod = mod['VerkMod']
        #verkmod['default_folder'] = str(self.verkmod_default_edit.text())
        #verkmod['executable'] = str(self.verkmod_exec_edit.text())

        config.write()
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