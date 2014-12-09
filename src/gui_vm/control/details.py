# -*- coding: utf-8 -*-
from gui_vm.view.resource_ui import Ui_DetailsResource
from gui_vm.view.scenario_ui import Ui_DetailsScenario
from gui_vm.view.project_ui import Ui_DetailsProject
from gui_vm.control.dialogs import CopyFilesDialog
from PyQt4 import QtGui, QtCore
from gui_vm.config.config import Config
from functools import partial
import os

config = Config()
config.read()

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

class ScenarioDetails(QtGui.QGroupBox, Ui_DetailsScenario):
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

    def __init__(self, simrun_node):
        super(ScenarioDetails, self).__init__()
        self.setupUi(self)
        self.setTitle(simrun_node.name)
        self.simrun_node = simrun_node
        self.combo_model.addItems(config.settings['trafficmodels'].keys())
        index = self.combo_model.findText(self.simrun_node.model.name)
        self.combo_model.setCurrentIndex(index)
        self.combo_model.currentIndexChanged['QString'].connect(
            self.changeModel)
        label = QtGui.QLabel('\n\nKenngroessen:\n')
        self.formLayout.addRow(label)
        for meta in simrun_node.meta:
            label = QtGui.QLabel(meta)
            txt = simrun_node.meta[meta]
            if isinstance(txt, list):
                txt = '<br>'.join(txt)
                edit = QtGui.QTextEdit(txt)
            else:
                edit = QtGui.QLineEdit(str(simrun_node.meta[meta]))
            edit.setReadOnly(True)
            self.formLayout.addRow(label, edit)

    def changeModel(self, name):
        '''
        change the traffic model
        '''
        self.simrun_node.set_model(str(name))
        self.value_changed.emit()

    def run(self):
        reply = dialog.question(
            self, _fromUtf8('Simulation starten'),
            _fromUtf8('Soll die Simulation gestartet werden?'),
            QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Ok:
            self.simrun_node.run()



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

    def __init__(self, project_node):
        super(ProjectDetails, self).__init__()
        self.setupUi(self)
        self.project_node = project_node
        self.setTitle(project_node.name)
        label = QtGui.QLabel('\n\nMetadaten:\n')
        self.meta_layout.addRow(label)
        for meta in project_node.meta:
            label = QtGui.QLabel(meta)
            edit = QtGui.QLineEdit(project_node.meta[meta])
            edit.setReadOnly(False)
            edit.textChanged.connect(
                partial((lambda key, value:
                         self.project_node.set_meta(key, str(value))),
                        meta))
            self.meta_layout.addRow(label, edit)
        self.folder_edit.setText(str(self.project_node.project_folder))

        #self.folder_browse_button.clicked.connect(self.browse_folder)
        self.folder_edit.textChanged.connect(self.update)

    def update(self):
        '''
        update the project view if sth was changed
        '''
        self.project_node.project_folder = (str(self.folder_edit.text()))
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

    def __init__(self, resource_node):
        super(ResourceDetails, self).__init__()
        self.setupUi(self)
        self.project_copy.setText(str(resource_node.full_source))
        self.file_edit.setText(str(resource_node.original_source))
        self.setTitle(resource_node.name)
        self.resource_node = resource_node
        self.browse_button.clicked.connect(self.browse_files)
        #self.file_edit.textChanged.connect(self.update)
        self.status_button.clicked.connect(self.get_status)
        self.show_attributes()

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
        attr = self.resource_node.resource.status
        build_tree(attr)
        self.resource_tree.resizeColumnToContents(0)
        #update the project view
        self.value_changed.emit()

    def browse_files(self):
        '''
        open a file browser to change the source of the resource file
        '''
        current = self.resource_node.full_source
        if not current:
            current = config.settings['trafficmodels'][
                self.resource_node.model.name]['default_folder'] + '/*.h5'
        fileinput = str(
            QtGui.QFileDialog.getOpenFileName(
                self, _fromUtf8('Ressourcendatei öffnen'),
                current))
        #filename is '' if aborted
        if len(fileinput) > 0:
            self.file_edit.setText(fileinput)
            self.update_source()

    def update_source(self):
        '''
        change the resource, copy the file
        '''
        src_filename = str(self.file_edit.text())
        self.resource_node.set_source(src_filename)
        dest_filename = self.resource_node.full_source
        self.project_copy.setText(dest_filename)
        self.value_changed.emit()
        #only try to copy file, if not the same file as before is selected
        if os.path.normpath(src_filename) != os.path.normpath(dest_filename):
            dialog = CopyFilesDialog(src_filename,
                                     self.resource_node.full_path,
                                     parent=self)
        self.resource_node.update()
        self.show_attributes()

    def get_status(self):
        '''
        validate the resource files
        '''
        self.resource_node.validate()
        self.show_attributes()

    def __del__(self):
        pass
