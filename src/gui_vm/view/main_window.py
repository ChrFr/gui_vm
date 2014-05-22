# -*- coding: utf-8 -*-
import sys
from gui_vm.view.qt_designed.main_window_ui import Ui_MainWindow
from PyQt4 import QtGui, QtCore
from project_view import ProjectTreeControl
from gui_vm.view.qt_designed.new_project_ui import Ui_NewProject
from gui_vm.view.qt_designed.progress_ui import Ui_ProgressDialog
from gui_vm.view.qt_designed.welcome_ui import Ui_Welcome
from gui_vm.model.backend import hard_copy
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
        self.project_tree_control = ProjectTreeControl()
        self.project_tree_view.setModel(self.project_tree_control)
        self.update_view()
        self.details = None

        #connect the buttons
        self.minus_button.clicked.connect(self.add_run)
        self.plus_button.clicked.connect(self.update_view)
        self.save_button.clicked.connect(self.save_project)
        self.open_button.clicked.connect(self.load_project)

        for button in self.context_button_group.children():
            button.setEnabled(False)

        #connect the tool bar
        self.actionProjekt_speichern.triggered.connect(self.save_project)
        self.actionProjekt_ffnen.triggered.connect(self.load_project)
        self.actionNeues_Szenario.triggered.connect(self.add_run)
        self.actionNeues_Projekt.triggered.connect(self.create_project)
        self.actionBeenden.triggered.connect(QtGui.qApp.quit)

        self.row_index = 0
        self.project_tree_view.clicked[QtCore.QModelIndex].connect(
            self.project_tree_control.row_changed)
        self.project_tree_control.dataChanged.connect(self.update_view)
        self.project_tree_control.details_changed.connect(self.update_view)
        self.project_changed.connect(self.update_view)
        welcome = WelcomeDialog(self)

    def add_run(self):
        project = self.project_tree_control.project
        text, ok = QtGui.QInputDialog.getText(
            self, 'Neues Szenario', 'Name des neuen Szenarios:',
            QtGui.QLineEdit.Normal,
            'Szenario {}'.format(project.child_count))
        if ok:
            name = str(text)
            if name in project.children_names:
                QtGui.QMessageBox.about(
                    self, "Fehler",
                    _fromUtf8("Der Szenarioname '{}' ist bereits vergeben."
                              .format(name)))
            else:
                project.add_run(model='Maxem', name=name)
                self.update_view()

    def remove_run(self):
        node_name = self.project_tree_view.model().data(
            self.row_index, QtCore.Qt.UserRole).name
        project = self.project_tree_control.project.remove_run(node_name)
        self.project_changed.emit()
        #select first row
        root_index = self.project_tree_control.createIndex(
            0, 0, self.project_tree_control.project)
        self.project_tree_view.setCurrentIndex(root_index)
        self.row_changed(root_index)

    def create_project(self):
        '''
        create a new project
        return True if new project was created
        '''
        project_name, project_folder, ok = NewProjectDialog.getValues()
        if ok:
            #close old project
            self.project_tree_control = ProjectTreeControl()
            self.project_tree_control.create_project(project_name)
            self.project_tree_control.project.project_folder = project_folder
            self.project_tree_view.setModel(self.project_tree_control)
            self.update_view()
            #select first row
            root_index = self.project_tree_control.createIndex(
                0, 0, self.project_tree_control.project)
            self.project_tree_view.setCurrentIndex(root_index)
            self.row_changed(root_index)
            return True
        else:
            return False

    def load_project(self):
        '''
        load a project
        return True if project was loaded
        '''
        fileinput = str(QtGui.QFileDialog.getOpenFileName(
            self, _fromUtf8('Projekt öffnen'), '.', '*.xml'))
        if len(fileinput) > 0:
            if self.project_tree_control.project:
                self.project_tree_control.project.remove()
            self.project_tree_control.read_project(fileinput)
            self.project_tree_control.project.update()
            self.project_changed.emit()
            return True
        else:
            return False

    def save_project(self):
        '''
        save the project
        '''
        filename = str(QtGui.QFileDialog.getSaveFileName(
            self, 'Projekt speichern', '.', '*.xml'))
        #filename is '' if aborted (file dialog returns no status)
        if len(filename) > 0:
            #get first project (by now only 1 project is displayed)
            #need to change, if there are more
            self.project_tree_control.write_project(filename)
            QtGui.QMessageBox.about(
                self, "Speichern erfolgreich",
                'Die Speicherung des Projektes\n{}\n war erfolgreich'.
                format(filename))

    def update_view(self):
        '''
        refresh the view on the project tree
        '''
        #self.project_tree_view.setModel(self.project_tree)
        self.project_tree_view.expandAll()
        for column in range(self.project_tree_view.model()
                            .columnCount(QtCore.QModelIndex())):
            self.project_tree_view.resizeColumnToContents(column)
        details = self.project_tree_control.details
        if details is not None:
            self.details_layout.addWidget(details)
            details.show()

    def rename(self):
        node = self.project_tree_view.model().data(self.row_index,
                                                   QtCore.Qt.UserRole)
        if node.rename:
            text, ok = QtGui.QInputDialog.getText(
                self, 'Umbenennen', 'Neuen Namen eingeben:',
                QtGui.QLineEdit.Normal, node.name)
            if ok:
                node.name = str(text)
                self.project_changed.emit()

    def remove_resource(self):
        '''
        remove the source of the resource node and optionally remove it from
        the disk
        '''
        node = self.project_tree_view.model().data(
            self.row_index, QtCore.Qt.UserRole)
        if os.path.exists(node.full_source):
            reply = QtGui.QMessageBox.question(
                None, _fromUtf8("Löschen"),
                _fromUtf8("Soll die Datei {} \nin {}\n".format(
                    node.resource.file_name, node.full_path) +
                          "ebenfalls entfernt werden?"),
                QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            do_delete = reply == QtGui.QMessageBox.Yes
            if do_delete:
                os.remove(node.full_source)
        node.set_source(None)
        node.update()
        self.project_changed.emit()

    def reset_simrun(self):
        '''
        set the simrun to default, copy all files from the default folder
        to the project/scenario folder and link the project tree to those
        files
        '''
        #self.project_tree_view.reset(self.row_index)
        simrun_node = self.project_tree_view.model().data(self.row_index,
                                                          QtCore.Qt.UserRole)
        simrun_node = simrun_node.reset_to_default()
        filenames = []
        destinations = []
        for res_node in simrun_node.get_resources():
            filenames.append(res_node.original_source)
            destinations.append(os.path.join(res_node.full_path))

        self.project_tree_view.setUpdatesEnabled(False)
        dialog = CopyFilesDialog(filenames, destinations, parent=self)
        self.project_tree_view.setUpdatesEnabled(True)
        #dialog.deleteLater()
        simrun_node.update()
        self.update_view()

    def reset_resource(self):
        res_node = self.project_tree_view.model().data(self.row_index,
                                                       QtCore.Qt.UserRole)
        res_node.reset_to_default()
        filename = res_node.original_source
        destination = res_node.full_path
        dialog = CopyFilesDialog(filename, destination, parent=self)
        #dialog.deleteLater()
        res_node.update()
        self.update_view()


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
        self.buttonBox.clicked.connect(self.close)
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
        self.progress_bar.setValue(100)

    def __del__(self):
        print 'messagebox geloescht'

