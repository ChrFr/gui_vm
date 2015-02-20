# -*- coding: utf-8 -*-
from gui_vm.view.progress_ui import Ui_ProgressDialog
from gui_vm.view.new_project_ui import Ui_NewProject
from gui_vm.view.new_scenario_ui import Ui_NewScenario
from gui_vm.view.special_run_ui import Ui_SpecialRun
from gui_vm.view.settings_ui import Ui_Settings
from gui_vm.model.backend import hard_copy, get_free_space
from PyQt4 import QtGui, QtCore
import sys, os
import re
from gui_vm.config.config import Config

config = Config()
config.read()

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
        super(CopyFilesDialog, self).__init__(parent=parent)
        self.parent = parent
        self.setupUi(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.startButton.hide()
        self.cancelButton.clicked.connect(self.close)
        self.show()
        self.copy(filenames, destinations)

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
                        self.cancelButton.setText('OK')
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
            self.cancelButton.setText('OK')
            self.progress_bar.setValue(100)


class ExecDialog(QtGui.QDialog, Ui_ProgressDialog):

    def __init__(self, scenario, run_name, options=None, parent=None):
        super(ExecDialog, self).__init__(parent=parent)
        self.parent = parent
        self.run_name = run_name
        self.scenario = scenario
        self.options = options
        self.setupUi(self)
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
        doStart = True
        primary = self.scenario.primary_run
        # there are already results after a successful run
        # a new run might be unnessecary, if file is present
        if primary and self.run_name == primary.name:
            dialog = QtGui.QMessageBox()
            msg = 'Das Szenario {} '.format(self.scenario.name) + \
                'wurde scheinbar bereits einmal komplett berechnet.\n' + \
                'Wollen Sie trotzdem einen erneuten Gesamtlauf starten?'
            reply = dialog.question(
                self, _fromUtf8("erneuter Gesamtlauf"), _fromUtf8(msg),
                QtGui.QMessageBox.Ok, QtGui.QMessageBox.Cancel)
            if reply == QtGui.QMessageBox.Cancel:
                doStart = False

        if doStart:
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

    def finished(self):
        # strange: process returns 1 even if successful
        #if not self.process.Crashed:
        self.progress_bar.setValue(100)
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

class SpecialRunDialog(QtGui.QDialog):
    '''
    open a dialog to define the parameters for a special run
    '''

    def __init__(self, scenario_node, stored_options=None, parent=None):
        super(SpecialRunDialog, self).__init__(parent=parent)
        self.setupUi()
        self.scenario = scenario_node
        self.option_checks = {}
        self.parent = parent

        def create_tab(opt_name, check_names, stored_options):
            tab = QtGui.QWidget()
            tab.setObjectName(_fromUtf8("area_types"))
            grid_layout = QtGui.QGridLayout(tab)
            scroll_area = QtGui.QScrollArea(tab)
            scroll_area.setWidgetResizable(True)
            grid_layout.addWidget(scroll_area, 0, 0, 1, 1)
            self.tabWidget.addTab(tab, _fromUtf8(opt_name))

            widget = QtGui.QWidget()
            layout = QtGui.QVBoxLayout()
            checks = []
            for i, name in enumerate(check_names[0]):
                checkbox = QtGui.QCheckBox(_fromUtf8(name))

                #check the boxes which are stored in options
                if stored_options and stored_options.has_key(opt_name)\
                   and check_names[1][i] in stored_options[opt_name]:
                    checkbox.setChecked(True)
                layout.addWidget(checkbox)
                checks.append(checkbox)
            layout.addSpacerItem(QtGui.QSpacerItem(20,40,
                    QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding))
            widget.setLayout(layout)
            scroll_area.setWidget(widget)
            return dict(zip(check_names[1], checks))

        model_options = self.scenario.model.options
        for opt, names in model_options.items():
            self.option_checks[opt] = create_tab(opt, names, stored_options)
        self.show()

    def setupUi(self):
        self.setObjectName(_fromUtf8("SpecialRun"))
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

    def retranslateUi(self, SpecialRun):
        SpecialRun.setWindowTitle(_translate("SpecialRun", "spezifischer Lauf", None))

    @staticmethod
    def getValues(scenario_node, stored_options=None):
        dialog = SpecialRunDialog(
            scenario_node, stored_options=stored_options)
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
            lambda: self.set_folder(self.maxem_default_edit))
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
        self.auto_python_button.clicked.connect(lambda: self.python_edit.setText(sys.executable))
        self.fill()
        self.show()

    def fill(self):
        env = config.settings['environment']

        self.python_edit.setText(env['python_path'])
        self.hdf5_edit.setText(env['hdf5_viewer'])

        mod = config.settings['trafficmodels']
        maxem = mod['Maxem']
        self.maxem_default_edit.setText(maxem['default_folder'])
        self.maxem_exec_edit.setText(maxem['executable'])

        #verkmod = mod['VerkMod']
        #self.verkmod_default_edit.setText(verkmod['default_folder'])
        #self.verkmod_exec_edit.setText(verkmod['executable'])


    def set_file(self, line_edit, extension):
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
        env['python_path'] = str(self.python_edit.text())
        env['hdf5_viewer'] = str(self.hdf5_edit.text())

        mod = config.settings['trafficmodels']
        maxem = mod['Maxem']
        maxem['default_folder'] = str(self.maxem_default_edit.text())
        maxem['executable'] = str(self.maxem_exec_edit.text())

        #verkmod = mod['VerkMod']
        #verkmod['default_folder'] = str(self.verkmod_default_edit.text())
        #verkmod['executable'] = str(self.verkmod_exec_edit.text())

        config.write()
        self.close()

    def reset(self):
        config.reset()