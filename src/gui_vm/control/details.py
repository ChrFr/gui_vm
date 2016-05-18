# -*- coding: utf-8 -*-

##------------------------------------------------------------------------------
## File:        project_control.py
## Purpose:     controls the interactions with the detail-views
##
## Author:      Christoph Franke
##
## Created:
## Copyright:   Gertz Gutsche Rümenapp - Stadtentwicklung und Mobilität GbR
##------------------------------------------------------------------------------

from gui_vm.view.resource_ui import Ui_DetailsResource
from gui_vm.view.scenario_ui import Ui_DetailsScenario
from gui_vm.view.project_ui import Ui_DetailsProject
from gui_vm.model.resources import Status
from gui_vm.model.project_tree import TreeNode
from gui_vm.control.dialogs import (CopyFilesDialog, RunOptionsDialog,
                                    InputDialog, ExecDialog, set_directory)
from PyQt4 import QtGui, QtCore
from gui_vm.config.config import Config
from functools import partial
import os

config = Config()

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

def clear_layout(layout):
    for i in reversed(range(layout.count())):
        item = layout.itemAt(i)
        # item has children -> is a layout itself, recursive call
        if isinstance(item, QtGui.QLayout):
            clear_layout(item)
        widget = item.widget()
        if widget:
            widget.deleteLater()


class ScenarioDetails(QtGui.QGroupBox, Ui_DetailsScenario):
    '''
    display the details of a simrun node in the given layout
    input to change the traffic model

    Parameters
    ----------
    node: Scenario,
          node, that contains the informations about a single scenario and it's resources
    layout: QVBoxLayout,
            the elements showing the details are added as children of this
            layout
    '''

    value_changed = QtCore.pyqtSignal([TreeNode])

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
        self.primary_button.clicked.connect(
            lambda: self.primary_run())
        self.special_button.clicked.connect(self.special_run)
        if scenario_node.locked:
            self.primary_button.setEnabled(False)
            self.special_button.setEnabled(False)
            self.combo_model.setEnabled(False)
        for meta in scenario_node.meta:
            label = QtGui.QLabel(_fromUtf8(meta))
            tooltip = scenario_node.meta[meta][1]
            txt = scenario_node.meta[meta][0]
            if isinstance(txt, list):
                txt = '<br>'.join(txt)
                edit = QtGui.QTextEdit(txt)
                edit.setMinimumHeight(100)
            else:
                edit = QtGui.QLineEdit(_fromUtf8(str(txt)))
            edit.setReadOnly(True)
            label.setToolTip(tooltip)
            edit.setToolTip(tooltip)
            self.data_form.addRow(label, edit)

    def special_run(self):
        run_node = self.project_control.add_special_run(self.scenario)

    def changeModel(self, name):
        '''
        change the traffic model
        '''
        self.scenario.set_model(str(name))
        self.value_changed.emit(self.scenario)

    def primary_run(self):
        self.project_control.add_primary_run(self.scenario)


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
    value_changed = QtCore.pyqtSignal([TreeNode])

    def __init__(self, project_node):
        super(ProjectDetails, self).__init__()
        self.setupUi(self)
        self.project_node = project_node
        self.setTitle(project_node.name)
        self.folder_edit.setText(str(self.project_node.project_folder))
        #self.folder_browse_button.clicked.connect(lambda: set_directory(self, self.folder_edit))
        self.folder_edit.textChanged.connect(self.update)
        self.add_meta_button.clicked.connect(self.add_meta)
        self.reload_meta()

    def reload_meta(self):
        clear_layout(self.meta_layout)

        for meta in self.project_node.meta:
            self.add_meta_row(meta, self.project_node.meta[meta])

    def add_meta_row(self, meta, meta_value):
        label = QtGui.QLabel(meta)
        edit = QtGui.QLineEdit(meta_value)
        edit.setReadOnly(False)
        edit.textChanged.connect(
            partial((lambda key, value:
                     self.project_node.set_meta(key, unicode(value.toUtf8(), encoding="UTF-8"))),
                    meta))
        self.meta_layout.addRow(label, edit)
        layout = QtGui.QHBoxLayout()
        layout.addWidget(edit)
        # you should not edit or delete certain fields (ToDo: define it in project)
        if meta == 'Uhrzeit' or meta == 'Datum':
            edit.setReadOnly(True)
        elif meta != 'Beschreibung' and meta != 'Autor':
            minus_button = QtGui.QPushButton(self.gridLayoutWidget)
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/buttons/icons/minus.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            minus_button.setIcon(icon)
            layout.addWidget(minus_button)
            minus_button.clicked.connect(partial(self.remove_meta, meta))
        self.meta_layout.addRow(label, layout)

    def update(self):
        '''
        update the project view if sth was changed
        '''
        self.project_node.project_folder = (str(self.folder_edit.text()))
        #self.value_changed.emit()

    def add_meta(self):
        meta, ok = QtGui.QInputDialog.getText(
            None, 'Metadaten', _fromUtf8('Name des neuen Felds:'),
            QtGui.QLineEdit.Normal, '')
        if ok:
            error_msg = ''
            meta = str(meta)
            if len(meta) == 0:
                error_msg = 'Sie haben keinen Namen für das Feld angegeben!'
            if self.project_node.meta.has_key(meta):
                error_msg = 'Das Feld "{}" ist bereits vorhanden!'.format(meta)
            if error_msg:
                QtGui.QMessageBox.about(None, "Fehler", _fromUtf8(error_msg))
                return
            self.project_node.set_meta(meta, '')
            self.add_meta_row(meta, '')

    def remove_meta(self, meta):
        self.project_node.remove_meta(meta)
        self.reload_meta()

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
    value_changed = QtCore.pyqtSignal([TreeNode])

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
            self.browse_button.clicked.connect(self.change_source)
            self.edit_button.clicked.connect(
                lambda: self.project_control.open_resource(self.resource_node))
            self.remove_button.clicked.connect(
                lambda: self.project_control.remove_resource(self.resource_node))
        #self.file_edit.textChanged.connect(self.update)

        # edit button disabled at the moment, many other ways to edit file via ui (try not to confuse the user)
        self.edit_button.setVisible(False)

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
            if status in [Status.NOT_FOUND, Status.MISMATCH]:
                status_color = red
            elif status in [Status.FOUND, Status.CHECKED_AND_VALID]:
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
                tooltip = line + ' ' + message
                item.setToolTip(0, tooltip)
                item.setToolTip(1, tooltip)
                item.setFont(0, font)
                if status in [Status.CHECKED_AND_VALID, Status.NOT_FOUND, Status.MISMATCH]:
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

    def change_source(self):
        '''
        open a file browser to change the source of the resource file
        '''
        fileinput = self.project_control.change_resource(self.resource_node)
        if not fileinput:
            return
        self.value_changed.emit(self.resource_node)

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
    value_changed = QtCore.pyqtSignal([TreeNode])

    def __init__(self, output_node, project_control, func_evaluate):
        super(OutputDetails, self).__init__(output_node.name)
        self.output = output_node
        self.resize(450, 309)
        self.project_control = project_control
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
        if output_node.locked:
            start_button.setEnabled(False)
            special_button.setEnabled(False)
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
            self.value_changed.emit(self.output)

    def run(self):
        self.project_control.run(self.output.scenario, run_name=self.output.name, options=self.output.options)