# -*- coding: utf-8 -*-
from gui_vm.view.qt_designed.progress_ui import Ui_ProgressDialog
from gui_vm.view.qt_designed.new_project_ui import Ui_NewProject
from gui_vm.view.qt_designed.new_simrun_ui import Ui_NewSimRun
from gui_vm.model.backend import hard_copy
from PyQt4 import QtGui, QtCore
import sys
from gui_vm.config.config import Config
import os

config = Config()
config.read()

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

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
        for i in xrange(len(filenames)):
            d, filename = os.path.split(filenames[i])
            dest_filename = os.path.join(destinations[i], filename)
            do_copy = True
            if os.path.exists(dest_filename):
                reply = QtGui.QMessageBox.question(
                    self, _fromUtf8("Überschreiben"),
                    _fromUtf8("Die Datei {} existiert bereits."
                              .format(filename) +
                              "\nWollen Sie sie überschreiben?"),
                    QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
                do_copy = reply == QtGui.QMessageBox.Yes
            if do_copy:
                status_txt = 'Kopiere <b>{}</b> nach <b>{}</b> ...<br>'.format(
                    filename, destinations[i])
                self.log_edit.insertHtml(status_txt)
                success = hard_copy(filenames[i], dest_filename,
                                    callback=self.progress_bar.setValue)
                if success:
                    status_txt = '{} erfolgreich kopiert<br>'.format(filename)
                else:
                    status_txt = ('<b>Fehler</b> beim Kopieren von {}<br>'
                                  .format(filename))
                self.log_edit.insertHtml(status_txt)
            else:
                status_txt = '<b>{}</b> nicht kopiert<br>'.format(
                    filename, destinations[i])
                self.log_edit.insertHtml(status_txt)
        self.cancelButton.setText('OK')
        self.progress_bar.setValue(100)


class ExecDialog(QtGui.QDialog, Ui_ProgressDialog):

    def __init__(self, simrun, parent=None):
        super(ExecDialog, self).__init__(parent=parent)
        self.parent = parent
        self.simrun = simrun
        self.setupUi(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.cancelButton.clicked.connect(self.close)
        self.startButton.clicked.connect(self.call_cmd)

        # QProcess object for external app
        self.process = QtCore.QProcess(self)

        # Just to prevent accidentally running multiple times
        # Disable the button when process starts, and enable it when it finishes
        self.process.started.connect(self.running)
        self.process.finished.connect(self.stopped)
        self.show()

    def call_cmd(self):
        # run the process
        self.simrun.model.run(self.simrun.name,
                              self.process,
                              self.simrun.get_resources(),
                              callback=self.show_status)

    def running(self):
        self.startButton.setEnabled(False)
        self.cancelButton.setText('Stoppen')
        self.cancelButton.clicked.disconnect(self.close)
        self.cancelButton.clicked.connect(self.kill)

    def stopped(self):
        self.startButton.setEnabled(True)
        self.cancelButton.setText(_fromUtf8('Schließen'))
        self.cancelButton.clicked.disconnect(self.kill)
        self.cancelButton.clicked.connect(self.close)

    def kill(self):
        self.process.kill()

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
        default = config.settings['environment']['default_project_folder']
        self.folder_edit.setText(default)
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
                return (project_name, project_folder, True)
            else:
                QtGui.QMessageBox.about(
                    dialog, "Warnung!", "Verzeichnis {} existiert nicht!"
                    .format(project_folder))
        return (project_name, project_folder, False)


class NewSimRunDialog(QtGui.QDialog, Ui_NewSimRun):
    '''
    open a dialog to set the scenario name and traffic model to work with
    '''

    def __init__(self, default_name):
        super(NewSimRunDialog, self).__init__()
        self.setupUi(self)
        self.name_edit.setText(default_name)
        self.combo_model.addItems(config.settings['trafficmodels'].keys())
        self.show()

    @staticmethod
    def getValues(default_name=''):
        dialog = NewSimRunDialog(default_name)
        ok = dialog.exec_()
        simrun_name = str(dialog.name_edit.text())
        model_name = str(dialog.combo_model.currentText())
        accepted = ok == QtGui.QDialog.Accepted
        return (simrun_name, model_name, accepted)