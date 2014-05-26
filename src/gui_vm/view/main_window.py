# -*- coding: utf-8 -*-
import sys
from gui_vm.view.qt_designed.main_window_ui import Ui_MainWindow
from PyQt4 import QtGui, QtCore
from project_view import ProjectTreeView
from gui_vm.view.qt_designed.new_project_ui import Ui_NewProject
from gui_vm.view.qt_designed.welcome_ui import Ui_Welcome
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

        #activation of buttons depending on the selected item
        self.project_view.editable[bool].connect(
            self.edit_button.setEnabled)
        self.project_view.addable[bool].connect(
            self.plus_button.setEnabled)
        self.project_view.removable[bool].connect(
            self.minus_button.setEnabled)
        self.project_view.resetable[bool].connect(
            self.reset_button.setEnabled)
        for button in self.context_button_group.children():
            button.setEnabled(False)
        #self.project_view.refreshable[bool].connect(
            #self.edit_button.setEnabled)

        #connect the tool bar
        self.actionProjekt_speichern.triggered.connect(self.save_project)
        self.actionProjekt_ffnen.triggered.connect(self.load_project)
        self.actionNeues_Szenario.triggered.connect(
            self.project_view.add_run)
        self.actionNeues_Projekt.triggered.connect(self.create_project)
        self.actionBeenden.triggered.connect(QtGui.qApp.quit)

        self.project_view.dataChanged.connect(self.project_changed_handler)
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
            #close old project
            self.project_view.create_project(project_name, project_folder)
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
            do_continue = True
            if self.project_has_changed:
                do_continue = self.project_changed_message()
            if do_continue:
                self.project_view.read_project(fileinput)
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
            do_continue = True
            if self.project_has_changed:
                do_continue = self.project_changed_message()
            if do_continue:
                self.project_view.write_project(filename)
                QtGui.QMessageBox.about(
                    self, "Speichern erfolgreich",
                    'Die Speicherung des Projektes\n{}\n war erfolgreich'.
                    format(filename))
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
        reply = QtGui.QMessageBox.question(
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


#class ProjectChangedDialogclass(QtGui.QWidget):
    #def __init__(self, parent=None):
        #QtGui.QWidget.__init__(self, parent)

        #self.setGeometry(300, 300, 350, 80)
        #self.setWindowTitle(_fromUtf8('Projekt geändert'))
        #self.label = QtGui.QLabel('Das Projekt wurde geändert.\n' +
                                  #'Wollen Sie die Änderungen speichern?')

        #self.label = QtGui.QLineEdit(self)
        #self.label.move(130, 22)
        #self.yes_button = QtGui.QPushButton('Ja', self)
        #self.no_button = QtGui.QPushButton('Nein', self)
        #self.cancel_button = QtGui.QPushButton('Abbrechen', self)
        ##self.yes_button.setFocusPolicy(QtCore.Qt.NoFocus)

        #self.yes_button.move(100, 200)
        #self.yes_button.clicked.connect(self.parent.save_project)
        #self.no_button.clicked.connect()
        #self.setFocus()


    #def showDialog(self):
        #text, ok = QtGui.QInputDialog.getText(self,
                                              #'Input Dialog', 'Enter your name:')

        #if ok:
            #self.label.setText(unicode(text))

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
