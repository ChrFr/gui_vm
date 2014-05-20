# -*- coding: utf-8 -*-
import sys
from gui_vm.view.qt_designed.main_window_ui import Ui_MainWindow
from PyQt4 import QtGui, QtCore
from project_view import ProjectTreeModel
from gui_vm.view.qt_designed.resource_ui import Ui_DetailsResource
from gui_vm.view.qt_designed.simrun_ui import Ui_DetailsSimRun
from gui_vm.view.qt_designed.project_ui import Ui_DetailsProject
from gui_vm.view.qt_designed.new_project_ui import Ui_NewProject
from gui_vm.view.qt_designed.progress_ui import Ui_ProgressDialog
from gui_vm.view.qt_designed.welcome_ui import Ui_Welcome
from gui_vm.config.config import DEFAULT_FOLDER
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
        self.project_tree = ProjectTreeModel()
        self.project_tree_view.setModel(self.project_tree)
        self.refresh_view()
        self.details = None

        #connect the buttons
        self.minus_button.clicked.connect(self.add_run)
        self.plus_button.clicked.connect(self.refresh_view)
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
            self.row_changed)
        self.project_tree.dataChanged.connect(self.refresh_view)
        self.project_changed.connect(self.refresh_view)
        welcome = WelcomeDialog(self)

    def row_changed(self, index):
        '''
        show details when row of project tree is clicked
        details shown depend on type of node that is behind the clicked row
        '''
        node = self.project_tree_view.model().data(index, QtCore.Qt.UserRole)
        #clicked highlighted row
        if self.row_index == index:
            #rename node if allowed
            self.rename()
        #clicked another row
        else:
            self.row_index = index
            #clear the old details
            if self.details:
                self.details.close()
            #reset all context dependent buttons
            self.button_group_label.setText('')
            for button in self.context_button_group.children():
                button.setEnabled(False)
                button.setToolTip('')
                try:
                    button.clicked.disconnect()
                except:
                    pass

            if node.rename:
                self.edit_button.setEnabled(True)
                self.edit_button.clicked.connect(self.rename)
                self.edit_button.setToolTip('Umbenennen')

            #show details and set buttons depending on type of node
            if node.__class__.__name__ == 'Project':
                self.button_group_label.setText('Projekt bearbeiten')

                self.plus_button.setEnabled(True)
                self.plus_button.setToolTip(_fromUtf8('Szenario hinzufügen'))
                self.plus_button.clicked.connect(self.add_run)

                self.details = ProjectDetails(node, self.details_layout)

            elif node.__class__.__name__ == 'SimRun':
                self.button_group_label.setText('Szenario bearbeiten')

                self.minus_button.setEnabled(True)
                self.minus_button.setToolTip(_fromUtf8('Szenario löschen'))
                self.minus_button.clicked.connect(self.remove_run)

                self.plus_button.setEnabled(True)
                self.plus_button.setToolTip(_fromUtf8('Szenario hinzufügen'))
                self.plus_button.clicked.connect(self.add_run)

                self.reset_button.setEnabled(True)
                self.reset_button.clicked.connect(self.reset_simrun)
                self.reset_button.setToolTip(
                    _fromUtf8('Default wiederherstellen'))

                self.details = SimRunDetails(node, self.details_layout)

            elif node.__class__.__name__ == 'ResourceNode':
                self.button_group_label.setText('Ressource bearbeiten')

                self.minus_button.setEnabled(True)
                self.minus_button.setToolTip(_fromUtf8('Ressource löschen'))
                self.minus_button.clicked.connect(self.remove_resource)

                self.reset_button.setEnabled(True)
                self.reset_button.clicked.connect(self.reset_resource)
                self.reset_button.setToolTip(
                    _fromUtf8('Default wiederherstellen'))

                self.details = ResourceDetails(node, self.details_layout)

            if self.details:
                self.details.value_changed.connect(self.refresh_view)

    def add_run(self):
        project = self.project_tree.project
        text, ok = QtGui.QInputDialog.getText(
            self, 'Neues Szenario', 'Name des neuen Szenarios:',
            QtGui.QLineEdit.Normal,
            'Szenario {}'.format(project.child_count()))
        if ok:
            name = str(text)
            project.add_run(model='Maxem', name=name)
            self.refresh_view()

    def remove_run(self):
        node_name = self.project_tree_view.model().data(
            self.row_index, QtCore.Qt.UserRole).name
        project = self.project_tree.project.remove_run(node_name)
        self.project_changed.emit()

    def create_project(self):
        '''
        create a new project
        return True if new project was created
        '''
        project_name, project_folder, ok = NewProjectDialog.getValues()
        if ok:
            self.project_tree.create_project(project_name)
            self.project_tree.project.project_folder = project_folder
            self.project_tree_view.setModel(self.project_tree)
            self.refresh_view()
            #select first row
            root_index = self.project_tree.createIndex(
                0, 0, self.project_tree.project)
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
            self.project_tree.read_project(fileinput)
            self.refresh_view()
            #select first row
            root_index = self.project_tree.createIndex(
                0, 0, self.project_tree.project)
            self.project_tree_view.setCurrentIndex(root_index)
            self.row_changed(root_index)
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
            self.project_tree.write_project(filename)
            QtGui.QMessageBox.about(
                self, "Speichern erfolgreich",
                'Die Speicherung des Projektes\n{}\n war erfolgreich'.
                format(filename))

    def refresh_view(self):
        '''
        refresh the view on the project tree
        '''
        self.project_tree_view.expandAll()
        for column in range(self.project_tree_view.model()
                            .columnCount(QtCore.QModelIndex())):
            self.project_tree_view.resizeColumnToContents(column)

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
        pass

    def reset_simrun(self, node):
        '''
        set the simrun to default, copy all files from the default folder
        to the project/scenario folder and link the project tree to those
        files
        '''
        node = self.project_tree_view.model().data(self.row_index,
                                                   QtCore.Qt.UserRole)
        model_name = node.model.name
        model_default_folder = os.path.join(DEFAULT_FOLDER, model_name)
        default_project_file = os.path.join(model_default_folder,
                                            'default.xml')
        default_project = ProjectTreeModel()
        default_project.read_project(default_project_file)
        default_model = default_project.root.find_all(model_name)[0]
        resource_nodes = default_model.find_all_by_classname('ResourceNode')
        for res_node in resource_nodes:
            res_name = res_node.name
            #node = self.project_tree.f

    def reset_resource(self):
        pass


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
        folder, ok = str(
            QtGui.QFileDialog.getExistingDirectory(
                self, 'Projektverzeichnis wählen', '.'))
        #filename is '' if aborted
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


class SimRunDetails(QtGui.QGroupBox, Ui_DetailsSimRun):
    '''
    display the details of a simrun node in the given layout
    input to change the traffic model

    Parameters
    ----------
    node: SimRun,
          node, that contains the
    layout: QVBoxLayout,
            the elements showing the details are added as children of this
            layout
    '''

    value_changed = QtCore.pyqtSignal()

    def __init__(self, node, parent):
        super(SimRunDetails, self).__init__()
        self.setupUi(self)
        self.parent = parent
        self.parent.addWidget(self)
        self.setTitle(node.name)
        self.node = node
        self.combo_model.addItems(self.node._available)
        index = self.combo_model.findText(self.node.model.name)
        self.combo_model.setCurrentIndex(index)
        self.combo_model.currentIndexChanged['QString'].connect(
            self.changeModel)
        label = QtGui.QLabel('\n\nKenngroessen:\n')
        self.formLayout.addRow(label)
        for meta in node.meta:
            label = QtGui.QLabel(meta)
            txt = node.meta[meta]
            if isinstance(txt, list):
                txt = '<br>'.join(txt)
                edit = QtGui.QTextEdit(txt)
            else:
                edit = QtGui.QLineEdit(str(node.meta[meta]))
            edit.setReadOnly(True)
            self.formLayout.addRow(label, edit)
        self.show()

    def changeModel(self, name):
        '''
        change the traffic model
        '''
        self.node.set_model(str(name))
        self.value_changed.emit()


class ProjectDetails(QtGui.QGroupBox, Ui_DetailsProject):
    '''
    display the details of a resource node in the given layout
    change the traffic model

    Parameters
    ----------
    node: Project,
          node, that contains the project information
    layout: QVBoxLayout,
            the elements showing the details are added as children of this
            layout
    '''
    value_changed = QtCore.pyqtSignal()

    def __init__(self, node, parent):
        super(ProjectDetails, self).__init__()
        self.setupUi(self)
        self.node = node
        self.parent = parent
        self.parent.addWidget(self)
        self.setTitle(node.name)
        label = QtGui.QLabel('\n\nMetadaten:\n')
        self.meta_layout.addRow(label)
        for meta in node.meta:
            label = QtGui.QLabel(meta)
            edit = QtGui.QLineEdit(node.meta[meta])
            edit.setReadOnly(True)
            self.meta_layout.addRow(label, edit)
        self.folder_edit.setText(self.node.project_folder)

        self.folder_browse_button.clicked.connect(self.browse_folder)
        self.folder_edit.textChanged.connect(self.update)
        self.show()

    def update(self):
        '''
        update the project view if sth was changed
        '''
        self.node.project_folder = (str(self.folder_edit.text()))
        self.value_changed.emit()

    def browse_folder(self):
        '''
        open a file browser to set the project folder
        '''
        folder = str(
            QtGui.QFileDialog.getExistingDirectory(
                self, 'Projektverzeichnis wählen', '.'))
        #filename is '' if aborted
        if len(folder) > 0:
            self.folder_edit.setText(folder)


class ResourceDetails(QtGui.QGroupBox, Ui_DetailsResource):
    '''
    display the details of a resource node
    input to change the source of the resource

    Parameters
    ----------
    node: ResourceNode,
          node, that wraps a resource and contains the file path of the
          resource
    layout: QVBoxLayout,
            the elements showing the details are added as children of this
            layout
    '''
    value_changed = QtCore.pyqtSignal()

    def __init__(self, node, parent):
        super(ResourceDetails, self).__init__()
        self.setupUi(self)
        self.parent = parent
        self.parent.addWidget(self)
        self.node = node
        self.project_copy.setText(str(self.node.full_source))
        self.file_edit.setText(str(self.node.original_source))
        self.setTitle(node.name)
        self.browse_button.clicked.connect(self.browse_files)
        #self.file_edit.textChanged.connect(self.update)
        self.status_button.clicked.connect(self.get_status)
        self.show_attributes()
        self.show()

    def show_attributes(self):
        '''
        show all available information of the resource node
        (incl. all child resources)
        '''

        def get_status_color(status):
            '''
            get a status color depending on given the status flag

            Return
            ------
            status_color: QtGui.QColor
            '''
            green = QtGui.QColor('green')
            red = QtGui.QColor('red')
            black = QtGui.QColor('black')
            if status in [3, 4]:
                status_color = red
            elif status in [1, 2]:
                status_color = green
            else:
                status_color = black

            return status_color

        def build_tree(attr, level=0, parent=self.resource_tree):
            '''
            build a resource tree out of a nested dictionary and view it
            '''
            normal = QtGui.QFont("Arial", 10-(level))
            bold = QtGui.QFont("Arial", 10-(level), QtGui.QFont.Bold)
            for key in attr:
                value, message, status = attr[key]
                status_color = get_status_color(status)

                if isinstance(value, dict):
                    val = ''
                    font = bold
                    has_subdict = True
                else:
                    val = value
                    font = normal
                    has_subdict = False

                line = ('{name}: {value}'
                        .format(name=key, value=val))
                status_color = get_status_color(status)
                item = QtGui.QTreeWidgetItem(parent, [line, message])
                item.setFont(0, font)
                if status in [2, 3, 4]:
                    item.setTextColor(0, status_color)
                item.setTextColor(1, status_color)
                if level == 0:
                    item.setExpanded(True)
                if has_subdict:
                    #recursion if there are sub dictionaries
                    build_tree(value, level+1, parent=item)

        self.resource_tree.clear()
        header = QtGui.QTreeWidgetItem(['Ressourcenbrowser', 'Status'])
        self.resource_tree.setHeaderItem(header)
        attr = self.node.resource.status
        build_tree(attr)
        self.resource_tree.resizeColumnToContents(0)
        #update the project view
        self.value_changed.emit()

    def browse_files(self):
        '''
        open a file browser to change the source of the resource file
        '''
        fileinput = str(
            QtGui.QFileDialog.getOpenFileName(
                self, _fromUtf8('Ressourcendatei öffnen'), DEFAULT_FOLDER))
        #filename is '' if aborted
        if len(fileinput) > 0:
            self.file_edit.setText(fileinput)
            self.update_source()

    def update_source(self):
        '''
        change the resource, copy the file
        '''
        self.node.set_source(str(self.file_edit.text()))
        self.project_copy.setText(str(self.node.full_source))
        self.value_changed.emit()
        dialog = CopyFilesDialog(str(self.file_edit.text()),
                                 self.node.full_path,
                                 parent=self)
        self.node.update()
        self.show_attributes()

    def get_status(self):
        '''
        validate the resource files
        '''
        self.node.resource.validate(self.node.simrun_path)
        self.show_attributes()

    def __del__(self):
        pass


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
        self.setupUi(self)
        self.setMaximumHeight(420)
        self.show()
        if not hasattr(filenames, '__iter__'):
            filenames = [filenames]
        if not hasattr(destinations, '__iter__'):
            destinations = [destinations]
        for i in xrange(len(filenames)):
            d, filename = os.path.split(filenames[i])
            status_txt = 'Kopiere <b>{}</b> nach <b>{}</b> ...<br>'.format(
                filename, destinations[i])
            self.log_edit.insertHtml(status_txt)
            dest_filename = os.path.join(destinations[i], filename)
            success = hard_copy(filenames[i], dest_filename,
                                callback=self.progress_bar.setValue)
            if success:
                status_txt = '{} erfolgreich kopiert<br>'.format(filename)
            else:
                status_txt = ('<b>Fehler</b> beim Kopieren von {}<br>'
                              .format(filename))
            self.log_edit.insertHtml(status_txt)

