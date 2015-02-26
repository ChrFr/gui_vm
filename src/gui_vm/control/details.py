# -*- coding: utf-8 -*-
from gui_vm.view.resource_ui import Ui_DetailsResource
from gui_vm.view.scenario_ui import Ui_DetailsScenario
from gui_vm.view.project_ui import Ui_DetailsProject
from gui_vm.control.dialogs import (CopyFilesDialog, RunOptionsDialog,
                                    InputDialog, ExecDialog)
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

    def __init__(self, scenario_node, project_control):
        super(ScenarioDetails, self).__init__()
        self.setupUi(self)
        self.setTitle(scenario_node.name)
        self.scenario = scenario_node
        self.project_control = project_control
        self.combo_model.addItems(config.settings['trafficmodels'].keys())
        index = self.combo_model.findText(self.scenario.model.name)
        self.combo_model.setCurrentIndex(index)
        self.combo_model.currentIndexChanged['QString'].connect(
            self.changeModel)
        self.start_button.clicked.connect(
            lambda: self.run())
        self.special_button.clicked.connect(self.special_run)
        label = QtGui.QLabel(_fromUtf8('\n\nKenngrössen:\n'))
        self.formLayout.addRow(label)
        for meta in scenario_node.meta:
            label = QtGui.QLabel(_fromUtf8(meta))
            txt = scenario_node.meta[meta]
            if isinstance(txt, list):
                txt = '<br>'.join(txt)
                txt = unicode(txt, "ISO-8859-1").encode('ascii', 'xmlcharrefreplace')
                edit = QtGui.QTextEdit(txt)
                edit.setMinimumHeight(100)
            else:
                edit = QtGui.QLineEdit(_fromUtf8(str(scenario_node.meta[meta])))
            edit.setReadOnly(True)
            self.formLayout.addRow(label, edit)

    def special_run(self):
        prime_run = self.scenario.primary_run
        if not prime_run:
            msg = _fromUtf8('Sie müssen zunächst einen Gesamtlauf durchführen!')
        elif prime_run.file_absolute is None or not prime_run.is_valid:
            msg = _fromUtf8('Der Gesamtlauf ist fehlerhaft! ' +
                            'Bitte erneut ausführen.')
        # only call dialog, if scenario is already calculated once and demand
        # file still exists
        else:
            options, ok = RunOptionsDialog.getValues(self.scenario)
            if ok:
                default = 'spezifischer Lauf {}'.format(
                    len(self.scenario.get_output_files()) - 1)
                run_name, ok = InputDialog.getValues(_fromUtf8(
                    'Name für den spezifischen Lauf'), default)
                if ok:
                    dialog = ExecDialog(self.scenario, run_name,
                                        options=options)
            return
        msgBox = QtGui.QMessageBox()
        msgBox.setText(msg)
        msgBox.exec_()


    def changeModel(self, name):
        '''
        change the traffic model
        '''
        self.scenario.set_model(str(name))
        self.value_changed.emit()

    def run(self):
        dialog = QtGui.QMessageBox()
        reply = dialog.question(
            self, _fromUtf8('Simulation starten'),
            _fromUtf8('Soll die Simulation gestartet werden?'),
            QtGui.QMessageBox.Ok, QtGui.QMessageBox.Cancel)
        if reply == QtGui.QMessageBox.Ok:
            self.project_control.run_complete(self.scenario)



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
        #self.value_changed.emit()

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


class InputDetails(QtGui.QGroupBox, Ui_DetailsResource):
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

    def __init__(self, resource_node, project_control):
        super(InputDetails, self).__init__()
        self.setupUi(self)
        self.project_control = project_control
        self.setTitle(resource_node.name)
        self.resource_node = resource_node
        if resource_node.locked:
            self.edit_button.setDisabled(True)
            self.remove_button.setDisabled(True)
            self.browse_button.setDisabled(True)
        else:
            self.browse_button.clicked.connect(self.browse_files)
            self.edit_button.clicked.connect(
                lambda: self.project_control.edit_resource(self.resource_node))
            self.remove_button.clicked.connect(
                lambda: self.project_control.remove_resource(self.resource_node))
        #self.file_edit.textChanged.connect(self.update)
        self.status_button.clicked.connect(self.get_status)
        self.setMinimumSize(500, 0)
        self.update()

    def update(self):
        self.project_copy.setText(str(self.resource_node.file_absolute))
        self.file_edit.setText(str(self.resource_node.original_source))
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
                item = QtGui.QTreeWidgetItem(parent, [line, _fromUtf8(message)])
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
        attr = self.resource_node.status
        if attr:
            build_tree(attr)
        self.resource_tree.resizeColumnToContents(0)

    def browse_files(self):
        '''
        open a file browser to change the source of the resource file
        '''
        current = self.resource_node.file_absolute
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
        self.resource_node.original_source = src_filename        
        self.resource_node.file_relative = os.path.join(
            self.resource_node.name, os.path.split(src_filename)[1])
        dest_filename = self.resource_node.file_absolute
        self.project_copy.setText(dest_filename)
        #only try to copy file, if not the same file as before is selected
        if os.path.normpath(src_filename) != os.path.normpath(dest_filename):
            dialog = CopyFilesDialog(src_filename,
                                     os.path.split(self.resource_node.file_absolute)[0],
                                     parent=self)
        self.resource_node.update()
        self.value_changed.emit()
        self.show_attributes()

    def get_status(self):
        '''
        validate the resource files
        '''
        self.resource_node.validate()
        self.show_attributes()


class OutputDetails(QtGui.QGroupBox):
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

    def __init__(self, output_node, func_evaluate):
        super(OutputDetails, self).__init__(output_node.name)
        self.output = output_node
        self.resize(450, 309)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setMinimumSize(QtCore.QSize(450, 0))
        self.formLayoutWidget = QtGui.QWidget(self)
        self.formLayoutWidget.setGeometry(QtCore.QRect(10, 80, 391, 221))
        self.formLayoutWidget.setObjectName(_fromUtf8("formLayoutWidget"))
        self.formLayout = QtGui.QFormLayout(self.formLayoutWidget)
        self.formLayout.setSizeConstraint(QtGui.QLayout.SetMinimumSize)
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setMargin(0)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))

        start_button = QtGui.QPushButton()
        start_button.setMinimumSize(QtCore.QSize(140, 0))
        start_button.setMaximumSize(QtCore.QSize(140, 100))
        start_button.setObjectName(_fromUtf8("start_button"))
        special_button = QtGui.QPushButton()
        special_button.setMinimumSize(QtCore.QSize(140, 0))
        special_button.setMaximumSize(QtCore.QSize(140, 100))
        special_button.setObjectName(_fromUtf8("special_button"))
        self.formLayout.addRow(start_button, special_button)
        start_button.setText('Start')
        special_button.setText('Optionen')
        self.formLayout.addRow(QtGui.QLabel(""))
        start_button.clicked.connect(self.run)
        special_button.clicked.connect(self.change_options)

        results = output_node.get_results()
        if results is None:
            self.formLayout.addRow(QtGui.QLabel('Keine Ergebnisse gefunden.'))
        else:
            for res in results:
                label = QtGui.QLabel(_fromUtf8(res))
                txt = results[res]
                if isinstance(txt, list):
                    txt = '<br>'.join(txt)
                    edit = QtGui.QLineEdit(_fromUtf8(txt))
                else:
                    edit = QtGui.QLineEdit(_fromUtf8(str(results[res])))
                edit.setReadOnly(True)
                self.formLayout.addRow(label, edit)

    def change_options(self):
        stored_options = self.output.options
        scenario = self.output.scenario
        new_options, ok = RunOptionsDialog.getValues(
            scenario, stored_options=stored_options,
            is_primary=self.output.is_primary)
        if ok:
            self.output.options = new_options
            scenario.project.emit()

    def run(self):
        scenario = self.output.scenario
        primary = scenario.primary_run
        if primary is None or (not self.output.is_primary and not primary.is_valid):
            msgBox = QtGui.QMessageBox()
            msgBox.setText(_fromUtf8('Der Gesamtlauf ist fehlerhaft! ' +
                                     'Bitte erneut ausführen.'))
            msgBox.exec_()
        else:
            dialog = ExecDialog(scenario, self.output.name,
                            options=self.output.options)