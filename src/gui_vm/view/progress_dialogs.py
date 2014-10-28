# -*- coding: utf-8 -*-
from gui_vm.view.qt_designed.progress_ui import Ui_ProgressDialog
from gui_vm.model.backend import hard_copy
from PyQt4 import QtGui, QtCore
import sys
import os

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
        self.setMaximumHeight(420)
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
        self.cancelButton.text('OK')
        self.progress_bar.setValue(100)


class ProgressDialog(QtGui.QDialog, Ui_ProgressDialog):

    def __init__(self, cmd, parent=None):
        super(ProgressDialog, self).__init__(parent=parent)
        self.parent = parent
        self.cmd = cmd
        self.setupUi(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setMaximumHeight(420)
        self.cancelButton.clicked.connect(self.kill)
        self.startButton.clicked.connect(self.callCmd)
        # QProcess object for external app
        self.process = QtCore.QProcess(self)
        # QProcess emits `readyRead` when there is data to be read
        self.process.readyReadStandardOutput.connect(self.showProgress)
        self.process.readyReadStandardError.connect(self.showProgress)

        # Just to prevent accidentally running multiple times
        # Disable the button when process starts, and enable it when it finishes
        self.process.started.connect(lambda: self.startButton.setEnabled(False))
        self.process.finished.connect(lambda: self.startButton.setEnabled(True))
        self.show()

    def callCmd(self):
        # run the process
        # `start` takes the exec and a list of arguments
        self.process.start(self.cmd)

    def kill(self):
        self.process.kill()

    def showProgress(self):
        status = self.process.readAllStandardError()
        self.log_edit.insertHtml( str(status) + '<br>')
        self.progress_bar.setValue(0)
