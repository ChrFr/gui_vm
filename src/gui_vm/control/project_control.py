# -*- coding: utf-8 -*-

##------------------------------------------------------------------------------
## File:        project_control.py
## Purpose:     controls all project-related interactions and delegates their
##              handling to the project-tree
##
## Author:      Christoph Franke
##
## Created:
## Copyright:   Gertz Gutsche Rümenapp - Stadtentwicklung und Mobilität GbR
##------------------------------------------------------------------------------

from PyQt4 import (QtCore, QtGui)
from gui_vm.control.details import (ScenarioDetails, ProjectDetails, InputDetails, OutputDetails)
from gui_vm.model.project_tree import (Project, TreeNode, Scenario,
                                       InputNode, XMLParser, OutputNode)
from gui_vm.control.dialogs import (CopyFilesDialog, ExecDialog,
                                    NewScenarioDialog, RunOptionsDialog,
                                    InputDialog, CopySpecialRunDialog)
from gui_vm.config.config import Config
import os, subprocess
from shutil import rmtree
import subprocess
from dialogs import browse_file, ALL_FILES_FILTER, HDF5_FILES_FILTER

config = Config()

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

class _Index(object):
    """representation of an index"""
    def __init__(self, qmodelindex):
        self.parent = qmodelindex.parent()
        self.row = qmodelindex.row()
        self.column = qmodelindex.column()

def disable_while_processing(function, parameter=None):
    config.mainWindow.setEnabled(False)
    config.mainWindow.repaint()
    function()
    config.mainWindow.setEnabled(True)


class ProjectTreeControl(QtCore.QAbstractItemModel):
    '''
    view on the project, holds the project itself and communicates with it,
    decides how to act on user input,
    also serves as an itemmodel to make the nodes showable in a qtreeview
    via indexing

    Parameter
    ---------
    parent: the window, where the dialogs will be shown in
    '''

    project_changed = QtCore.pyqtSignal()
    view_changed = QtCore.pyqtSignal()

    def __init__(self, view=None):
        super(ProjectTreeControl, self).__init__()
        self.tree_view = view
        self.tree_view.expanded.connect(lambda: self.tree_view.resizeColumnToContents(0))
        self.tree_view.collapsed.connect(lambda: self.tree_view.resizeColumnToContents(0))
        self.model = TreeNode('root')
        self.header = ('Projekt', 'Details')
        self.count = 0

    @property
    def current_index(self):
        return self.index(self._current_index.row,
                          self._current_index.column,
                          self._current_index.parent)

    @current_index.setter
    def current_index(self, value):
        self._current_index = _Index(value)

    @property
    def selected_item(self):
        if self.current_index is None:
            return None
        return self.nodeFromIndex(self.current_index)

    @property
    def project(self):
        return self.model.child_at_row(0)

    ##### overrides for viewing in qtreeview #####

    def headerData(self, section, orientation, role):
        if (orientation == QtCore.Qt.Horizontal and
            role == QtCore.Qt.DisplayRole):
            return QtCore.QVariant(self.header[section])
        return QtCore.QVariant()

    def index(self, row, column, parent_index):
        node = self.nodeFromIndex(parent_index)
        if row >= 0 and len(node.children) > row:
            return self.createIndex(row, column, node.child_at_row(row))
        else:
            return QtCore.QModelIndex()


    def data(self, index, role):
        '''
        return data to the tableview depending on the requested role
        '''
        node = self.nodeFromIndex(index)
        if node is None:
            return QtCore.QVariant()

        if role == QtCore.Qt.DecorationRole:
            return QtCore.QVariant()

        if role == QtCore.Qt.TextAlignmentRole:
            return QtCore.QVariant(
                int(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft))

        if role == QtCore.Qt.UserRole:
            return node

        #color the the columns of a node depending on its status
        if role == QtCore.Qt.TextColorRole:
            #if hasattr(node, 'is_checked'):
            is_checked = node.is_checked
            if is_checked:
                #if hasattr(node, 'is_valid'):
                is_valid = node.is_valid
                if is_valid:
                    if index.column() == 1:
                        return QtCore.QVariant(QtGui.QColor(QtCore.Qt.darkGreen))
                else:
                    return QtCore.QVariant(QtGui.QColor(QtCore.Qt.red))
            return QtCore.QVariant(QtGui.QColor(QtCore.Qt.black))

        if role == QtCore.Qt.FontRole:
            #if  (index.column() == 0 and
            if (isinstance(node, Scenario) or isinstance(node, Project)):
                return QtCore.QVariant(
                    QtGui.QFont("Arial", 9, QtGui.QFont.Bold))
            else:
                return QtCore.QVariant(QtGui.QFont("Arial", 9))

        #all other roles (except display role)
        if role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()

        #Display Role (text)
        if index.column() == 0:
            return QtCore.QVariant(node.name)

        elif index.column() == 1:
            return QtCore.QVariant(node.note)

        else:
            return QtCore.QVariant()

    def columnCount(self, parent):
        return len(self.header)

    def rowCount(self, parent):
        node = self.nodeFromIndex(parent)
        if node is None:
            return 0
        return node.child_count

    def parent(self, child_idx):
        if not child_idx.isValid():
            return QtCore.QModelIndex()

        node = self.nodeFromIndex(child_idx)

        if node is None or not isinstance(node, TreeNode):
            return QtCore.QModelIndex()

        try:
            parent = node.parent
        except AttributeError:
            print node
            print node.__class__
            print node.name
            raise

        if parent is None:
            return QtCore.QModelIndex()

        grandparent = parent.parent
        if grandparent is None:
            row = 0
        else:
            row = grandparent.row_of_child(parent)

        assert row != - 1
        return self.createIndex(row, 0, parent)

    def nodeFromIndex(self, index):
        return index.internalPointer() if index.isValid() else self.model

    def insertRow(self, row, parent):
        return self.insertRows(row, 1, parent)

    def insertRows(self, row, count, parent):
        self.beginInsertRows(parent, row, (row + (count - 1)))
        self.endInsertRows()
        return True

    def remove_row(self, row, parentIndex):
        return self.removeRows(row, 1, parentIndex)

    def removeRows(self, row, count, parentIndex):
        self.beginRemoveRows(parentIndex, row, row)
        node = self.nodeFromIndex(parentIndex)
        if node is not None and len(node.children) > row:
            node.remove_child_at(row)
        self.endRemoveRows()

        return True

    def pop_context_menu(self, pos):
        pass


class VMProjectControl(ProjectTreeControl):
    def __init__(self, view=None, details_view=None, button_group=None):
        super(VMProjectControl, self).__init__(view)
        self.details_view = details_view
        self.button_group = button_group
        self.plus_button = self.button_group.findChild(
            QtGui.QAbstractButton, 'plus_button')
        self.minus_button = self.button_group.findChild(
            QtGui.QAbstractButton, 'minus_button')
        self.edit_button = self.button_group.findChild(
            QtGui.QAbstractButton, 'edit_button')
        self.reset_button = self.button_group.findChild(
            QtGui.QAbstractButton, 'reset_button')
        self.lock_button = self.button_group.findChild(
            QtGui.QAbstractButton, 'lock_button')
        self.copy_button = self.button_group.findChild(
            QtGui.QAbstractButton, 'copy_button')
        self.clean_button = self.button_group.findChild(
            QtGui.QAbstractButton, 'clean_button')
        self.open_button = self.button_group.findChild(
            QtGui.QAbstractButton, 'context_open_button')

        self.view_changed.connect(self.update_view)
        self.dataChanged.connect(self.update_view)

        # connect the context buttons with the defined actions
        self.plus_button.clicked.connect(lambda: self.start_function('add'))
        self.minus_button.clicked.connect(lambda: self.start_function('remove'))
        self.edit_button.clicked.connect(lambda: self.start_function('edit'))
        self.open_button.clicked.connect(lambda: self.start_function('open'))
        self.reset_button.clicked.connect(lambda: self.start_function('reset'))
        #self.start_button.clicked.connect(self.project_control.execute)

        self.lock_button.clicked.connect(lambda:
                                         self.start_function('switch_lock'))

        self.copy_button.clicked.connect(lambda: self.start_function('copy'))

        self.project_changed.connect(self.item_clicked)

        for button in self.button_group.children():
            button.setEnabled(False)

        # map functions to defined actions
        # structure: keys are action names -
        #            values are dictionaries with class of node in context
        #               and [function to execute, tooltip/context-menu text, depending_on_lock (only active when node is unlocked)] as values
        self.context_map = {
            'add': {
                Project: [self.add_scenario, 'Szenario hinzufügen', True],
                Scenario: [self.add_run, 'Lauf hinzufügen', True],
                OutputNode: [self.add_special_run, 'spezifischen Lauf hinzufügen', True]
            },
            'remove': {
                Scenario: [self.remove_scenario, 'Szenario entfernen', True],
                InputNode: [self.remove_resource, 'Quelldatei entfernen', True],
                OutputNode: [self._remove_output, 'Quelldatei entfernen', True]
            },
            'reset': {
                Scenario: [self._reset_scenario, 'Szenario zurücksetzen', True],
                InputNode: [self._reset_resource, 'Eingabedaten zurücksetzen', True]
            },
            'open': {
                Scenario: [self._open_explorer, 'in Windows-Explorer anzeigen', False],
                Project: [self._open_explorer, 'in Windows-Explorer anzeigen', False],
                InputNode: [self.edit_resource, 'Quelldatei öffnen', True],
                OutputNode: [self.edit_resource, 'Quelldatei öffnen', True]
            },
            'edit': {
                Scenario: [self._rename_scenario, 'Szenario umbenennen', True],
                Project: [self._rename_node, 'Projekt umbenennen', True],
                InputNode: [self.change_resource, 'Quelldatei ändern', True],
                OutputNode: [self._edit_options, 'Optionen editieren', True]
            },
            'execute': {
                Scenario: [self.run, 'Gesamtlauf starten', True]
            },
            'switch_lock': {
                Scenario: [self._switch_lock, 'Szenario sperren', False],
            },
            'copy': {
                Scenario: [self.clone_scenario, 'Szenario klonen', False],
                OutputNode: [self._copy_special_run, 'spezifischen Lauf kopieren', True]
            },
            'clean': {

            },
            'other': {
                OutputNode: [self._open_explorer, 'in Windows-Explorer anzeigen', False],
                InputNode: [self._open_explorer, 'in Windows-Explorer anzeigen', False]
            },
        }

    def item_clicked(self, index=None):
        '''
        show details when row of project tree is clicked
        details shown depend on type of node that is behind the clicked row
        '''
        if index is not None:
            self.current_index = index
        self.dataChanged.emit(self.current_index, self.current_index)

    def select_node(self, node):
        '''
        emulate clicking and selecting the given node inside the tree view
        '''
        row = node.parent.get_row(node.name) if hasattr(node, 'parent') else 0
        index = self.createIndex(row, 0, node)
        self.item_clicked(index)
        self.tree_view.setCurrentIndex(index)

    def start_function(self, function_name):
        node = self.selected_item
        cls = node.__class__
        if cls in self.context_map[function_name]:
            disable_while_processing(self.context_map[function_name][cls][0])
        #self.project_changed.emit()

    def change_resource(self, input_node=None):
        '''
        let the user choose a resource file for the given input-node
        '''
        if not input_node:
            input_node = self.selected_item

        scenario = input_node.scenario

        if len(scenario.get_output_files()) > 0:
            reply = QtGui.QMessageBox.question(
                None, _fromUtf8("Zurücksetzen"),
                _fromUtf8('Wenn Sie die Ressource ändern, werden alle bestehenden Ausgaben ungültig und somit entfernt!'),
                QtGui.QMessageBox.Yes, QtGui.QMessageBox.Cancel)
            if reply == QtGui.QMessageBox.Cancel:
                return

        self.remove_outputs(scenario)

        #open a file browser to change the source of the resource file
        current_path = input_node.file_absolute
        if not current_path:
            current_path = config.settings['trafficmodels'][
                input_node.model.name]['default_folder']
        fileinput = browse_file(config.mainWindow, directory=current_path,
                                filters=[ALL_FILES_FILTER, HDF5_FILES_FILTER],
                                selected_filter_idx=1)
        #filename is '' if aborted
        if len(fileinput) == 0:
            return None

        input_node.original_source = fileinput
        input_node.file_relative = os.path.join(
            input_node.parent.name, os.path.split(fileinput)[1])
        dest_filename = input_node.file_absolute
        #only try to copy file, if not the same file as before is selected
        if os.path.normpath(fileinput) != os.path.normpath(dest_filename):
            dialog = CopyFilesDialog(fileinput,
                                     os.path.split(input_node.file_absolute)[0])
            dialog.exec_()
        input_node.update()
        return fileinput

    def _map_buttons(self, node):

        # emit signal flags for context
        locked = node.locked
        cls = node.__class__

        def map_button(button, map_name, depends_on_lock=False, condition=True):
            enabled = is_in_map = cls in self.context_map[map_name] and condition

            if is_in_map:
                depends_on_lock = self.context_map[map_name][cls][2]
                if depends_on_lock:
                    enabled = not locked
                tooltip = _fromUtf8(self.context_map[map_name][cls][1])
            else:
                tooltip = ''
            button.setEnabled(enabled)
            button.setToolTip(tooltip)

        map_button(self.plus_button,'add')
        map_button(self.minus_button, 'remove')
        condition = hasattr(node, "model") \
            and len(config.settings['trafficmodels'][node.model.name]['default_folder']) > 0
        map_button(self.reset_button, 'reset', condition=condition)
        map_button(self.edit_button, 'edit')
        map_button(self.open_button, 'open')
        #self.start_button.setEnabled(cls in self.context_map['execute'])
        map_button(self.lock_button, 'switch_lock')
        if node.locked:
            self.lock_button.setChecked(True)
        else:
            self.lock_button.setChecked(False)

        condition = not isinstance(node, OutputNode) or not node.is_primary
        map_button(self.copy_button, 'copy', condition=condition)
        map_button(self.clean_button, 'clean')

    def pop_context_menu(self, pos):
        #self.item_clicked(self.current_index)
        node = self.selected_item
        cls = node.__class__
        context_menu = QtGui.QMenu()
        action_map = {}
        for key, value in self.context_map.iteritems():
            if cls in value:
                depends_on_lock = value[cls][2]
                if not depends_on_lock or not node.locked:
                    action_map[context_menu.addAction(_fromUtf8(value[cls][1]))] = \
                        value[cls][0]
        #shows double details if not hidden
        for i in reversed(range(self.details_view.count())):
            widget = self.details_view.itemAt(i).widget()
            if widget: widget.hide()

        action = context_menu.exec_(self.tree_view.mapToGlobal(pos))
        context_menu.close()
        if action:
            action_map[action]()

    def update_view(self):
        #workaround: added nodes are not shown because not added the right way via insertRow(buggy)
        #-> collapse and expand project node (insert_row doesn't work)
        if self.project:
            index = self.createIndex(0, 0, self.project)
            self.tree_view.collapse(index)
            self.tree_view.expand(index)

        #clear the old details
        for i in reversed(range(self.details_view.count())):
            widget = self.details_view.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        #get new details depending on type of node
        node = self.selected_item
        if node is None:
            return

        details = None

        if isinstance(node, Project):
            details = ProjectDetails(node)
        elif isinstance(node, Scenario):
            details = ScenarioDetails(node, self)
        elif isinstance(node, InputNode):
            details = InputDetails(node, self)
        elif isinstance(node, OutputNode):
            details = OutputDetails(node, self, node.model.evaluate)

        #track changes made in details
        if details:
            details.value_changed.connect(self.view_changed)
            details.value_changed.connect(self.project_changed.emit)
            self.details_view.addWidget(details)
            details.update()

        self._map_buttons(node)

    def _edit_options(self, output_node=None):
        if not output_node:
            output_node = self.selected_item
        scenario_node = output_node.scenario
        options, ok = RunOptionsDialog.getValues(scenario_node, stored_options=output_node.options, is_primary=output_node.is_primary)
        if ok:
            output_node.options = options
            self.project_changed.emit()

    def _insert_node(self, row, column, node, parentIndex):
        new_index = self.createIndex(row, column, node)
        self.beginInsertRows(parentIndex, row, column)
        self.insertRow(row, parentIndex)
        self.endInsertRows()

    def _remove_node(self, node):
        if not node:
            node = self.selected_item
        row = node.parent.get_row(node.name)
        index = self.createIndex(row, 0, node)
        parent_idx = self.parent(index)

        if row == 0:
            prev_idx = parent_idx
        else:
            prev_idx = self.createIndex(row-1, 0, node.parent.children[row-1])
        self.item_clicked(prev_idx)
        self.tree_view.setCurrentIndex(prev_idx)

        self.remove_row(index.row(),
                        parent_idx)
        node.remove_all_children()

    def _open_explorer(self, path=None):
        if not path:
            if hasattr(self.selected_item, 'path'):
                path = self.selected_item.path
            elif hasattr(self.selected_item, 'project_folder'):
                path = self.selected_item.project_folder
            else:
                return
        if not os.path.exists(path):
            msg = _fromUtf8('Der Pfad "{}" existiert nicht'.format(path))
            dialog = QtGui.QMessageBox()
            dialog.setWindowTitle("Fehler")
            dialog.setText(msg)
            dialog.exec_()
            return
        subprocess.Popen(r'explorer "{}"'.format(os.path.normpath(path)))

    def _choose_scenario(self, text=""):
        combo_model = QtGui.QComboBox()

        scenario_names = [scen.name for scen in self.project.get_children()]

        if len(scenario_names) == 0:
            QtGui.QMessageBox.about(
                None, "Fehler",
                _fromUtf8("Keine Szenarios vorhanden!"))
            return None

        combo_model.addItems(scenario_names)

        name, ok = QtGui.QInputDialog.getItem(
                None, _fromUtf8('Szenario wählen'), text,
                scenario_names)
        if ok:
            return self.project.get_child(name)

        return None

    def _choose_run(self, scenario, text=""):
        combo_model = QtGui.QComboBox()

        run_names = [scen.name for scen in self.project.get_children()]

        if len(run_names) == 0:
            QtGui.QMessageBox.about(
                None, "Fehler",
                _fromUtf8("Keine spezifischen Läufe vorhanden!"))
            return None

        combo_model.addItems(scenario_names)

        name, ok = QtGui.QInputDialog.getItem(
                None, _fromUtf8('Szenario wählen'), text,
                scenario_names)
        if ok:
            return self.project.get_child(name)

        return None

    def remove_scenario(self, scenario_node=None, do_choose=False):

        if not scenario_node and not do_choose:
            scenario_node = self.selected_item
        if do_choose:
            scenario_node = self._choose_scenario(
                _fromUtf8('zu löschendes Szenario auswählen'))
        if scenario_node is None:
            return

        if scenario_node.locked:
            QtGui.QMessageBox.about(
                None, "Fehler",
                _fromUtf8("Das Szenario ist gesperrt und kann nicht " +
                          "gelöscht werden."))
            return

        path = scenario_node.path
        reply = QtGui.QMessageBox.question(
            None, _fromUtf8("Löschen"),
            _fromUtf8('Soll das gesamte Szenario-Verzeichnis "{}"\n'.format(
                path) + 'von der Festplatte entfernt werden?'),
            QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.No:
            return
        try:
            rmtree(scenario_node.path)
        except Exception, e:
            QtGui.QMessageBox.about(
            None, "Fehler", str(e))
        self._remove_node(scenario_node)
        self.project_changed.emit()


    def remove_resource(self, resource_node=None, remove_node=False,
                        confirmation=True, remove_outputs=True):
        '''
        remove the source of the resource node and optionally remove it from
        the disk
        '''
        if not resource_node:
            resource_node = self.selected_item
        if resource_node.locked:
            QtGui.QMessageBox.about(
                None, "Fehler",
                _fromUtf8("Die Ressource ist gesperrt und kann nicht " +
                          "gelöscht werden."))
            return
        file_absolute = resource_node.file_absolute
        if file_absolute and os.path.exists(file_absolute):
            do_delete = True
            if confirmation:
                reply = QtGui.QMessageBox.question(
                    None, _fromUtf8("Löschen"),
                    _fromUtf8('Soll die verknüpfte Datei "{}" \n'.format(file_absolute) +
                              'von der Festplatte entfernt werden?'),
                    QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
                do_delete = reply == QtGui.QMessageBox.Yes
            if do_delete:
                os.remove(resource_node.file_absolute)
        resource_node.file_relative = None
        if remove_node:
            self._remove_node(resource_node)
        else:
            resource_node.update()

        if remove_outputs:
            scenario = resource_node.scenario
            self.remove_outputs(scenario)
        self.project_changed.emit()

    def _remove_output(self, resource_node=None):
        if not resource_node:
            resource_node = self.selected_item

        scenario = resource_node.scenario
        if resource_node.is_primary:
            msg = "Soll der Gesamtlauf wirklich entfernt werden?"
            if len(scenario.get_output_files()) > 1:
                msg += "\nAlle spezifischen Läufe werden ebenfalls gelöscht!"
            reply = QtGui.QMessageBox.question(
                None, _fromUtf8("Löschen"), _fromUtf8(msg),
                QtGui.QMessageBox.Ok, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Ok:
                cur_tmp = self.current_index
                parent_idx = self.current_index.parent()
                self.item_clicked(parent_idx.parent())
                self.tree_view.setCurrentIndex(parent_idx.parent())
                self.remove_row(parent_idx.row(), parent_idx.parent())
                self.remove_outputs(scenario)
        else:
            self.remove_resource(remove_node=True, remove_outputs=False,
                                 confirmation=False)

    def run(self, scenario_node=None, do_choose=False, run_name=Scenario.PRIMARY_RUN, options=None):
        '''
        Parameter
        ---------
        do_choose: opens a dialog to choose the scenario, where to execute the run
        scenario_node: if not given, try to select
        '''
        if not scenario_node and not do_choose:
            scenario_node = self.selected_item
        if do_choose:
            scenario_node = self._choose_scenario(
                _fromUtf8('In welchem Szenario soll der Lauf ausgeführt werden?'))
        if scenario_node is None:
            return

        if scenario_node.locked:
            QtGui.QMessageBox.about(
                None, "Fehler",
                _fromUtf8("Das Szenario und seine Läufe sind gesperrt."))
            return

        dialog = QtGui.QMessageBox()
        if not scenario_node.is_valid:
            msg = _fromUtf8('Das Szenario ist fehlerhaft (rot markierte Felder).' +
                            'Der Lauf kann nicht gestartet werden.')
            dialog.setWindowTitle("Fehler")
            dialog.setText(msg)
            dialog.exec_()
            return

        if run_name != Scenario.PRIMARY_RUN:
            primary = scenario_node.primary_run
            if primary is None or not primary.is_valid:
                msgBox = QtGui.QMessageBox()
                msgBox.setWindowTitle(_fromUtf8('Fehler'))
                msgBox.setText(_fromUtf8('Der Gesamtlauf ist fehlerhaft! ' +
                                         'Bitte führen Sie ihn erneut aus, bevor Sie spezifische Läufe starten!'))
                msgBox.exec_()
                return

        if not options:
            options, ok = RunOptionsDialog.getValues(scenario_node, is_primary=run_name==Scenario.PRIMARY_RUN)
            if not ok:
                return
        dialog = ExecDialog(scenario_node, run_name,
                            parent=self.tree_view, options=options)
        dialog.exec_()

    def _switch_lock(self, resource_node=None):
        if not resource_node:
            resource_node = self.selected_item
        if resource_node.admin_locked and not config.admin_mode:
            self.lock_button.setChecked(True)
            msgBox = QtGui.QMessageBox()
            msgBox.setWindowTitle(_fromUtf8('Warnung'))
            msgBox.setText(_fromUtf8('Das Szenario wurde durch den Admin gesperrt und kann nur durch ihn entsperrt oder bearbeitet werden.'))
            msgBox.exec_()
            return
        resource_node.locked = not resource_node.locked
        if config.admin_mode:
            resource_node.admin_locked = resource_node.locked
        self.project_changed.emit()

    def _rename_node(self):
        node = self.selected_item
        name, ok = QtGui.QInputDialog.getText(
            None, 'Umbenennen', 'Neuen Namen eingeben:',
            QtGui.QLineEdit.Normal, node.name)
        if ok:
            node.name = str(name)
            self.project_changed.emit()

    def _rename_scenario(self, scenario_node=None):
        if not scenario_node:
            scenario_node = self.selected_item
        while True:
            name, ok = QtGui.QInputDialog.getText(
                None, 'Umbenennen', 'Neuen Namen eingeben:',
                QtGui.QLineEdit.Normal, scenario_node.name)
            if ok:
                if self.project.has_child(name):
                    QtGui.QMessageBox.about(
                        None, 'Fehler',
                        _fromUtf8('Das Projekt enthält bereits ein Szenario mit dem Namen "{}"'
                        .format(name)))
                    continue
                old_path = scenario_node.path
                scenario_node.name = str(name)
                try:
                    os.rename(old_path, scenario_node.path)
                except:
                    pass
                self.project_changed.emit()
                break
            else:
                break

    def _copy_special_run(self, output_node=None):
        if not output_node:
            output_node = self.selected_item
        new_name, scenario_name, ok = CopySpecialRunDialog.getValues(output_node)
        if ok:
            scenario = self.project.get_child(scenario_name)
            new_run = scenario.add_run(new_name, output_node.options)

    def clone_scenario(self, scenario_node=None, do_choose=False, new_scenario_name=None):
        if not scenario_node and not do_choose:
            scenario_node = self.selected_item

        if do_choose:
            scenario_node = self._choose_scenario(
                _fromUtf8('zu klonendes Szenario auswählen'))

        if scenario_node is None:
            return

        if not new_scenario_name:

            # get name of new scenario by dialog, if not passed
            text, ok = QtGui.QInputDialog.getText(
                        None, 'Szenario kopieren', 'Name des neuen Szenarios:',
                        QtGui.QLineEdit.Normal, scenario_node.name + ' - Kopie')
            if ok:
                new_scenario_name = str(text)
            else:
                return

        if new_scenario_name in self.project.children_names:
            QtGui.QMessageBox.about(
                None, "Fehler",
                _fromUtf8("Der Szenarioname '{}' ist bereits vergeben."
                          .format(new_scenario_name)))
            return

        new_scenario_node = scenario_node.clone(new_scenario_name)

        # reset the locks
        new_scenario_node.locked = False
        new_scenario_node.admin_locked = False

        scenario_node.parent.add_child(new_scenario_node)
        path = new_scenario_node.path
        if os.path.exists(new_scenario_node.path):
            reply = QtGui.QMessageBox.question(
                None, _fromUtf8('Fehler'),
                _fromUtf8('Der Pfad "{}" existiert bereits. Wollen Sie trotzdem fortsetzen?'
                              .format(path)),
                QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.No:
                return
        filenames = []
        destinations = []
        for i, nodes in enumerate([scenario_node.get_input_files(),
                                   scenario_node.get_output_files()]):
            is_input = i == 0
            for res_node in nodes:
                if is_input:
                    new_res_node = new_scenario_node.get_input(res_node.name)
                else:
                    new_res_node = new_scenario_node.get_output(res_node.name)
                if new_res_node and os.path.exists(res_node.file_absolute):
                    filenames.append(res_node.file_absolute)
                    destinations.append(os.path.split(new_res_node.file_absolute)[0])

        #bad workaround (as it has to know the parents qtreeview)
        #but the view crashes otherwise, maybe make update signal
        self.tree_view.setUpdatesEnabled(False)
        dialog = CopyFilesDialog(filenames, destinations)
                                 #parent=self.tree_view)
        self.tree_view.setUpdatesEnabled(True)
        self.project_changed.emit()

    def edit_resource(self, resource_node=None):
        if not resource_node:
            resource_node = self.selected_item
        node = self.selected_item
        hdf5_viewer = config.settings['environment']['hdf5_viewer']
        if hdf5_viewer:
            subprocess.Popen('"{0}" "{1}"'.format(hdf5_viewer,
                                                  node.file_absolute))
        else:
            QtGui.QMessageBox.about(
                None, "Fehler",
                _fromUtf8("In den Einstellungen ist kein HDF5-Editor angegeben."))

    def add_scenario(self):
        project = self.project
        if (not project):
            return
        default_name = 'Szenario {}'.format(project.child_count)
        scenario_name, model_name, ok = NewScenarioDialog.getValues(default_name)
        if ok:
            if scenario_name in project.children_names:
                QtGui.QMessageBox.about(
                    None, "Fehler",
                    _fromUtf8("Der Szenarioname '{}' ist bereits vergeben."
                              .format(scenario_name)))
            else:
                project.add_scenario(model=model_name, name=scenario_name)

                scenario_node=project.get_child(scenario_name)
                if not os.path.exists(scenario_node.path):
                    os.mkdir(scenario_node.path)
                if(len(config.settings['trafficmodels'][model_name]['default_folder']) > 0):
                    reply = QtGui.QMessageBox.question(
                        None, _fromUtf8("Neues Szenario erstellen"),
                        _fromUtf8("Möchten Sie die Standarddateien " +
                                  "für das neue Szenario verwenden?"),
                        QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
                    do_copy = reply == QtGui.QMessageBox.Yes
                    if do_copy:
                        self._reset_scenario(scenario_node, ask_overwrite=False)
                self.project_changed.emit()
                self.select_node(scenario_node)

    def add_run(self, scenario=None, do_choose=False):
        '''
        add a run to a scenario,
        adds primary run, if none is existing yet, adds special run else

        Parameter
        ---------
        scenario: scenario node, where run should be added
        do_choose: open dialog to let user choose scenario manually
        '''
        if not scenario and not do_choose:
            node = self.selected_item
            if isinstance(node, Scenario):
                scenario = node
            else:
                scenario = node.scenario
        if do_choose:
            scenario = self._choose_scenario(
                _fromUtf8('Zu welchem Szenario soll der Lauf hinzugefügt werden?'))
        if scenario is None:
            return

        if scenario.get_output(Scenario.PRIMARY_RUN) is None:
            self.add_primary_run(scenario=scenario)
        else:
            self.add_special_run(scenario=scenario)

    def add_primary_run(self, scenario=None, do_choose=False):
        if not scenario and not do_choose:
            node = self.selected_item
            if isinstance(node, Scenario):
                scenario = node
            else:
                scenario = node.scenario
        if do_choose:
            scenario = self._choose_scenario(
                _fromUtf8('Zu welchem Szenario soll der Lauf hinzugefügt werden?'))
        if scenario is None:
            return

        if scenario.locked:
            QtGui.QMessageBox.about(
                None, "Fehler",
                _fromUtf8("Es können keine Läufe zu gesperrten Szenarios hinzugefügt werden"))
            return

        if scenario.get_output(Scenario.PRIMARY_RUN) is not None:
            msg = _fromUtf8('Es existiert bereits ein ' + Scenario.PRIMARY_RUN)
            msgBox = QtGui.QMessageBox()
            msgBox.setText(msg)
            msgBox.exec_()
            return

        options, ok = RunOptionsDialog.getValues(scenario, is_primary=True)
        if not ok:
            return
        run_node = scenario.add_run(Scenario.PRIMARY_RUN, options)
        self.select_node(run_node)

    def add_special_run(self, scenario=None, do_choose=False):
        if not scenario and not do_choose:
            node = self.selected_item
            if isinstance(node, Scenario):
                scenario = node
            else:
                scenario = node.scenario
        if do_choose:
            scenario = self._choose_scenario(
                _fromUtf8('Zu welchem Szenario soll der Lauf hinzugefügt werden?'))
        if scenario is None:
            return

        if scenario.locked:
            QtGui.QMessageBox.about(
                None, "Fehler",
                _fromUtf8("Es können keine Läufe zu gesperrten Szenarios hinzugefügt werden"))
            return

        prime_run = scenario.primary_run
        if not prime_run:
            msg = _fromUtf8('Sie müssen zunächst einen Gesamtlauf durchführen!')
            msgBox = QtGui.QMessageBox()
            msgBox.setText(msg)
            msgBox.exec_()
            return
        elif prime_run.file_absolute is None or not prime_run.is_valid:
            msg = _fromUtf8('Der Gesamtlauf ist fehlerhaft! ' +
                            'Bitte führen Sie ihn erneut aus, bevor Sie einen neuen spezifischen Lauf anlegen!')
            msgBox = QtGui.QMessageBox()
            msgBox.setWindowTitle(_fromUtf8('Fehler'))
            msgBox.setText(msg)
            msgBox.exec_()
            return

        options, ok = RunOptionsDialog.getValues(scenario, is_primary = False)
        if ok:
            default = 'spezifischer Lauf {}'.format(
                len(scenario.get_output_files()) - 1)
            run_name, ok = InputDialog.getValues(_fromUtf8(
                'Name für den spezifischen Lauf'), default)
            if ok:
                scenario.add_run(run_name, options=options)

    def _reset_scenario(self, scenario_node=None, ask_overwrite=True):
        '''
        set the simrun to default, copy all files from the default folder
        to the project/scenario folder and link the project tree to those
        files
        '''
        if not scenario_node:
            scenario_node = self.selected_item

        if ask_overwrite:
            reply = QtGui.QMessageBox.question(
                        None, _fromUtf8("Zurücksetzen"),
                        _fromUtf8('Soll das gesamte Szenario "{}" inklusive der Ein- und Ausgaben auf die Standardwerte zurückgesetzt werden?'.format(scenario_node.name)),
                        QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.No:
                return

        success, message = scenario_node.reset_to_default()

        if not success:
            QtGui.QMessageBox.about(
                None, "Fehler",
                _fromUtf8(message))
        else:
            filenames = []
            destinations = []
            for res_node in scenario_node.get_input_files():
                filenames.append(res_node.original_source)
                destinations.append(os.path.split(res_node.file_absolute)[0])

            #bad workaround (as it has to know the parents qtreeview)
            #but the view crashes otherwise, maybe make update signal
            self.tree_view.setUpdatesEnabled(False)
            dialog = CopyFilesDialog(filenames, destinations)
            dialog.exec_()
            self.tree_view.setUpdatesEnabled(True)
            #dialog.deleteLater()
            scenario_node.update()
            self.remove_outputs(scenario_node)

        self.project_changed.emit()

    def validate_project(self):
        scenarios = self.project.find_all_by_class(Scenario)
        #for scen in scenarios:
            #scen.update()
        for scen in scenarios:
            scen.validate()
        self.view_changed.emit()

    def _reset_resource(self):
        res_node = self.selected_item

        scenario = res_node.scenario
        if len(scenario.get_output_files()) > 0:
            reply = QtGui.QMessageBox.question(
                None, _fromUtf8("Zurücksetzen"),
                _fromUtf8('Wenn Sie die Ressource zurücksetzen, werden alle bestehenden Ausgaben ungültig und somit entfernt!'),
                QtGui.QMessageBox.Yes, QtGui.QMessageBox.Cancel)
            if reply == QtGui.QMessageBox.Cancel:
                return
        else:
            reply = QtGui.QMessageBox.question(
                None, _fromUtf8("Zurücksetzen"),
                _fromUtf8('Soll die Ressource "{}" auf die Standardwerte zurückgesetzt werden?'.format(res_node.name)),
                QtGui.QMessageBox.Yes, QtGui.QMessageBox.Cancel)
            if reply == QtGui.QMessageBox.Cancel:
                return

        success, message = res_node.reset_to_default()

        if not success:
            QtGui.QMessageBox.about(
                None, "Fehler",
                _fromUtf8(message))
        else:
            filename = res_node.original_source
            destination = os.path.split(res_node.file_absolute)[0]
            dialog = CopyFilesDialog(filename, destination,
                                     parent=self.tree_view)
            res_node.update()
            scenario = res_node.scenario
            self.remove_outputs(scenario)
            self.project_changed.emit()

    def write_project(self, filename):
        XMLParser.write_xml(self.project, filename)

    def new_project(self, name, project_folder):
        if os.path.exists(os.path.join(project_folder, Project.FILENAME_DEFAULT)):
            QtGui.QMessageBox.about(
                None, "Fehler",
                _fromUtf8("Im Ordner ist bereits eine Projektdatei vorhanden! "
                          .format(project_folder)+
                          "Bitte wählen Sie ein anderes Verzeichnis oder"+
                          " löschen Sie vorher das vorhandene Projekt!"))
            return False
        if name is None:
            name = 'Neues Projekt'
        if self.project:
            self.close_project()
        self.model.add_child(Project(name, project_folder=project_folder))
        self.project.on_change(self.project_changed.emit)
        index = self.createIndex(0, 0, self.project)
        self.item_clicked(index)
        self.tree_view.setCurrentIndex(index)
        return True

    def close_project(self):
        self.current_index = self.createIndex(0, 0, self.project)
        if self.project:
            self._remove_node(self.project)
        self.view_changed.emit()

    def read_project(self, filename):
        self.close_project()
        XMLParser.read_xml(self.model, filename)
        self.project.on_change(self.project_changed.emit)
        self.project.project_folder = os.path.split(filename)[0]
        self.project.update()
        self.project_changed.emit()
        self.view_changed.emit()
        self.tree_view.resizeColumnToContents(0)
        self.select_node(self.project)

    def remove_outputs(self, scenario):
        for output in scenario.get_output_files():
            try:
                rmtree(os.path.split(output.file_absolute)[0])
            except:
                pass
        output = scenario.get_child(scenario.OUTPUT_NODES)
        if output:
            output.remove_all_children()