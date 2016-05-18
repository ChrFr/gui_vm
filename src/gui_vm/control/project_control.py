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
from gui_vm.control.details import (ScenarioDetails, ProjectDetails,
                                    InputDetails, OutputDetails)
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
    '''
    representation of an index
    '''
    def __init__(self, qmodelindex):
        self.parent = qmodelindex.parent()
        self.row = qmodelindex.row()
        self.column = qmodelindex.column()

def disable_while_processing(function):
    '''
    disable the main-window while executing given function

    Parameter
    ---------
    function: executable function
    '''
    config.mainWindow.setEnabled(False)
    config.mainWindow.repaint()
    function()
    config.mainWindow.setEnabled(True)


class ProjectTreeControl(QtCore.QAbstractItemModel):
    '''
    view on the project-tree, controls insertion and deletion of nodes,
    serves as an itemmodel to render the nodes in a qtreeview via indexing

    Parameter
    ---------
    view: the window, where the dialogs will be shown in
    '''
    # signals, that the project has changed (-> autosave)
    project_changed = QtCore.pyqtSignal()
    # signals, that nodes inside the project were changed (-> init validation)
    nodes_changed = QtCore.pyqtSignal([TreeNode])
    # signals, that the view should be updated
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
        '''
        get the index of the currently selected item
        '''
        try:
            self._current_index = _Index(value)
        except:
            return

    @property
    def selected_item(self):
        '''
        get the currently selected node
        '''
        if self.current_index is None:
            return None
        return self.nodeFromIndex(self.current_index)

    ##### overrides for viewing in qtreeview #####

    def headerData(self, section, orientation, role):
        '''
        get the data of the header, depending on role and column
        '''
        if (orientation == QtCore.Qt.Horizontal and
            role == QtCore.Qt.DisplayRole):
            return QtCore.QVariant(self.header[section])
        return QtCore.QVariant()

    def index(self, row, column, parent_index):
        '''
        get an index at given row and column relative to a parent index
        '''
        node = self.nodeFromIndex(parent_index)
        if row >= 0 and len(node.children) > row:
            return self.createIndex(row, column, node.child_at_row(row))
        else:
            return QtCore.QModelIndex()


    def data(self, index, role):
        '''
        return data to the table-view depending on the requested role at
        given index (= style and content of nodes at index), not meant to
        be called manually, is called by table-view only

        the returned QVariant defines the "style" and content used for the role
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

        # tooltip always shows the name of the node (ToDo: show error messages?)
        if role == QtCore.Qt.ToolTipRole:
            return QtCore.QVariant(node.name)

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
        '''
        get number of columns

        Parameter
        ---------
        parent: is obsolete, just taken in account here because of override)
        '''
        return len(self.header)

    def rowCount(self, index):
        '''
        get the number of child-nodes of node at given index

        Parameter
        ---------
        index: QModelIndex, index of the node
        '''
        node = self.nodeFromIndex(index)
        if node is None:
            return 0
        return node.child_count

    def parent(self, child_idx):
        '''
        get the parent index

        Parameter
        ---------
        child_idx: QModelIndex, index of the child
        '''
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
        '''
        get a node at the given index

        Parameter
        ---------
        index: QModelIndex, index of the node
        '''
        return index.internalPointer() if index.isValid() else self.model

    def insertRow(self, row, parent):
        '''
        insert single row

        Parameter
        ---------
        row:         number of the row where it is inserted
        parentindex: QModelIndex, index of parent node
        '''
        return self.insertRows(row, 1, parent)

    def insertRows(self, row, count, parent):
        '''
        insert multiple rows

        Parameter
        ---------
        row:         number of the row in relation to parent
        count:       number of rows to be inserted after given row
        parentindex: QModelIndex, index of parent node
        '''
        self.beginInsertRows(parent, row, (row + (count - 1)))
        self.endInsertRows()
        return True

    def remove_row(self, row, parentIndex):
        '''
        remove a row from the tree-view

        Parameter
        ---------
        row:         number of the row in relation to parent
        parentindex: QModelIndex, index of parent node
        '''
        return self.removeRows(row, 1, parentIndex)

    def removeRows(self, row, count, parentIndex):
        '''
        remove multiple rows from the tree-view

        Parameter
        ---------
        row:         number of the row in relation to parent
        count:       number of rows to be removed starting from given row
        parentindex: QModelIndex, index of parent node
        '''
        self.beginRemoveRows(parentIndex, row, row)
        node = self.nodeFromIndex(parentIndex)
        if node is not None and len(node.children) > row:
            node.remove_child_at(row)
        self.endRemoveRows()

        return True

    def pop_context_menu(self, pos):
        '''
        override this one, if you want to enable context menu
        '''
        pass

    def _insert_node(self, row, column, node, parentIndex):
        '''
        insert node at row, column relative to parentIndex
        '''
        new_index = self.createIndex(row, column, node)
        self.beginInsertRows(parentIndex, row, column)
        self.insertRow(row, parentIndex)
        self.endInsertRows()

    def _remove_node(self, node=None):
        '''
        remove a tree-node from the tree, removes all
        of it's child-nodes as well

        Parameter
        ---------
        node: optional, the node to be removed from the tree (if not given
              currently selected node is taken)
        '''
        if not node:
            node = self.selected_item
        row = node.parent.get_row(node.name)
        index = self.createIndex(row, 0, node)
        parent_idx = self.parent(index)

        if row == 0:
            prev_idx = parent_idx
        else:
            prev_idx = self.createIndex(row-1, 0, node.parent.children[row-1])
        self.select_item(prev_idx)
        self.tree_view.setCurrentIndex(prev_idx)

        self.remove_row(index.row(),
                        parent_idx)
        node.remove_all_children()

    def select_item(self, index=None):
        '''
        select an index (or current index) inside the tree-view and update
        the view

        Parameter
        ---------
        index: optional, index of the tree-item (if not given, current index is taken)
        '''
        if index is not None:
            self.current_index = index
        self.dataChanged.emit(self.current_index, self.current_index)

    def select_node(self, node):
        '''
        select and highlight a node inside the project-tree-view

        Parameter
        ---------
        node: the tree-node to be selected
        '''
        row = node.parent.get_row(node.name) if hasattr(node, 'parent') else 0
        index = self.createIndex(row, 0, node)
        self.select_item(index)
        self.tree_view.setCurrentIndex(index)


class VMProjectControl(ProjectTreeControl):
    '''
    extends the view on the project tree with contextual functions for scenario-
    and resource-management specific to the traffic-model. Is also specifically
    adapted to the qt-designed main-window with it's context buttons and layout
    to show the details of a selected node.

    Parameter
    ---------
    view:         a QTreeView where the project-tree is rendered in
    details_view: a QLayout where the details of a node are rendered in
    button_group: a QGroupBox containing buttons that will be mapped on functions
                  to interact with the project-tree (depending on the selected node)
    '''

    def __init__(self, view, details_view, button_group):
        super(VMProjectControl, self).__init__(view)

        # CONNECT SLOTS TO SIGNALS
        self.view_changed.connect(self.update_view)
        self.nodes_changed.connect(self.validate_nodes)
        # nodes changed -> project changed as well (save project in main_control)
        self.nodes_changed.connect(lambda: self.project_changed.emit())
        # dataChanged signals, that rows of the qtreeview have changed
        self.dataChanged.connect(self.update_view)

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

        # connect the context buttons with the defined actions
        self.plus_button.clicked.connect(lambda: self.context_function('add'))
        self.minus_button.clicked.connect(lambda: self.context_function('remove'))
        self.edit_button.clicked.connect(lambda: self.context_function('edit'))
        self.open_button.clicked.connect(lambda: self.context_function('open'))
        self.reset_button.clicked.connect(lambda: self.context_function('reset'))
        #self.start_button.clicked.connect(self.project_control.execute)

        self.lock_button.clicked.connect(lambda:
                                         self.context_function('switch_lock'))

        self.copy_button.clicked.connect(lambda: self.context_function('copy'))

        self.project_changed.connect(self.select_item)

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
                Scenario: [self._open_explorer, 'in Explorer anzeigen', False],
                Project: [self._open_explorer, 'in Explorer anzeigen', False],
                InputNode: [self.open_resource, 'Quelldatei öffnen', True],
                OutputNode: [self.open_resource, 'Quelldatei öffnen', True]
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
                Scenario: [self._switch_lock, 'Szenario sperren/entsperren', False],
            },
            'copy': {
                Scenario: [self.clone_scenario, 'Szenario klonen', False],
                OutputNode: [self._copy_special_run, 'Lauf kopieren', True]
            },
            'clean': {

            },
            'other': {
                OutputNode: [self._open_explorer, 'in Explorer anzeigen', False],
                InputNode: [self._open_explorer, 'in Explorer anzeigen', False]
            },
        }

    @property
    def project(self):
        '''
        get the project-node (node in first row)
        '''
        return self.model.child_at_row(0)

    def context_function(self, function_name):
        '''
        map a the name of a function to an assigned function in the context_map
        depending on the currently selected node

        Parameter
        ---------
        fucntion_name: the name of the function (key of context_map)
        '''
        node = self.selected_item
        cls = node.__class__
        if cls in self.context_map[function_name]:
            disable_while_processing(self.context_map[function_name][cls][0])
        #self.project_changed.emit()

    def change_resource(self, input_node=None):
        '''
        let the user choose a resource file for the given input-node, removes
        all outputs, because they depend on the inputs

        Parameter
        ---------
        input_node: optional, input-node, the resource of which will be changed
                   (if not given the currently selected item inside the project-tree is taken)
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
        self.nodes_changed.emit(input_node)
        return fileinput

    def _map_buttons(self, node):
        '''
        map a node to a buttons, meaning connect buttons to contextual functions
        allocated with the context_map, enable/disable them and set the tooltips

        Parameter
        ---------
        node: the tree-node, the button-functions are allocated to
        '''

        # emit signal flags for context
        locked = node.locked
        cls = node.__class__

        def map_button(button, map_name, depends_on_lock=False, condition=True):
            enabled = is_in_map = cls in self.context_map[map_name] and condition
            tooltip = ''

            if is_in_map:
                depends_on_lock = self.context_map[map_name][cls][2]
                tooltip = _fromUtf8(self.context_map[map_name][cls][1])
                if depends_on_lock:
                    enabled = not locked

            button.setEnabled(enabled)
            if not enabled:
                tooltip = ''
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
        '''
        pop a context menu, content depends on currently selected node

        Parameter
        ---------
        pos: QPoint, position where the context-menu is drawn on the screen
        '''
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

        action = context_menu.exec_(self.tree_view.mapToGlobal(pos))
        context_menu.close()
        if action:
            action_map[action]()

    def update_view(self):
        '''
        update the view on the project-tree and the details of the currently
        selected tree-item
        '''
        # workaround: added nodes are not shown because not added the correct way
        # via insertRow(buggy) -> collapse and expand project node
        if self.project:
            index = self.createIndex(0, 0, self.project)
            self.tree_view.collapse(index)
            self.tree_view.expand(index)

        #clear the old details
        for i in reversed(range(self.details_view.count())):
            widget = self.details_view.itemAt(i).widget()
            if widget:
                widget.deleteLater()
                # hide the widget, because deleteLater is lazy and causes
                # double widgets, if same node is selected again (e.g. when
                # popping context menu)
                widget.hide()

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
        '''
        change the options of an output-node (= run-options)

        Parameter
        ---------
        output_node: optional, the output_node (if not given the currently
                     selected item inside the project-tree is taken)
        '''
        if not output_node:
            output_node = self.selected_item
        scenario_node = output_node.scenario
        options, ok = RunOptionsDialog.getValues(scenario_node, stored_options=output_node.options, is_primary=output_node.is_primary)
        if ok:
            output_node.options = options
            self.project_changed.emit()

    def _open_explorer(self, path=None):
        '''
        open a path with the windows-explorer

        Parameter
        ---------
        path: optional, the path to be shown with the explorer (if not given
              the path to the currently selected node is taken)
        '''
        if not path:
            # resources have file paths
            if hasattr(self.selected_item, 'file_absolute'):
                path = os.path.split(self.selected_item.file_absolute)[0]
            # scenarios have paths
            elif hasattr(self.selected_item, 'path'):
                path = self.selected_item.path
            # projects only specify the root folder
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
        '''
        open a dialog to let the user select a scenario out of all scenarios
        of the currently opened project

        Parameter
        ---------
        text: optional, Text inside the dialog for choosing a scenario

        Return
        ---------
        the selected scenario-node,
        None, if no scenario was selected
        '''
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

    def remove_scenario(self, scenario_node=None, do_choose=False):
        '''
        remove a scenarion from currently opened project. Removes it's
        folder containing the resource-files from disk as well.

        Parameter
        ---------
        scenario: optional, scenario node, that will be removed(if not given
                  the currently selected item inside the project-tree is taken)
        do_choose: optional, open dialog to let user choose scenario manually
        '''
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
            _fromUtf8('Soll das Szenario "{}" entfernt werden?\n'
                      .format(scenario_node.name) +
                      'Achtung: das Verzeichnis "{}" '.format(path) +
                      'wird dabei ebenfalls von der Festplatte entfernt!'),
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
        remove the source-link of a resource node. ask the user if the
        linked file should be removed from disk as well. resource nodes may
        represent inputs and outputs.

        Parameter
        ---------
        resource_node:  optional, the resource-node whose resource shall be removed
                        (if not given the currently selected item inside the
                        project-tree is taken)
        confirmation:   optional, if True, asks the user if to delete the file,
                        deletes without asking else (default True)
        remove_node:    optional, if True, removes the node from project-tree (default False)
        remove_outputs: optional, if True, all output-nodes are removed from the parent
                        scenario, because the ouputs depend on the inputs (default True)

        '''
        if not resource_node:
            resource_node = self.selected_item

        scenario = resource_node.scenario
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
            self.remove_outputs(scenario)
        self.nodes_changed.emit(scenario)

    def _remove_output(self, output_node=None):
        '''
        remove an output-node from the project-tree and
        remove it's linked file from disk

        Parameter
        ---------
        output_node: optional, the output_node that shall be removed (if not given the
                     currently selected item inside the project-tree is taken)
        '''
        if not output_node:
            output_node = self.selected_item

        scenario = output_node.scenario
        if output_node.is_primary:
            msg = "Soll der Gesamtlauf wirklich entfernt werden?"
            if len(scenario.get_output_files()) > 1:
                msg += "\nAlle spezifischen Läufe werden ebenfalls gelöscht!"
            reply = QtGui.QMessageBox.question(
                None, _fromUtf8("Löschen"), _fromUtf8(msg),
                QtGui.QMessageBox.Ok, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Ok:
                self.remove_outputs(scenario)
        else:
            self.remove_resource(remove_node=True, remove_outputs=False,
                                 confirmation=False)

    def run(self, scenario_node=None, do_choose=False,
            run_name=Scenario.PRIMARY_RUN, options=None):
        '''
        execute a child-run of the given scenario

        Parameter
        ---------
        do_choose:     optional, opens a dialog to choose the scenario, where to execute the run
        scenario_node: optional, if not given, takes the selected node of the project-tree
        run_name:      optional, the name of the run to be executed (defaults to the primary run)
        options:       optional, the options the run will be executed with (usually command-line options),
                       if not given a dialog is opened to let the user select the options
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
        self.nodes_changed.emit(scenario_node)

    def _switch_lock(self, scenario_node=None):
        '''
        locks unlocked scenarios and unlocks locked scenarios. locked scenarios
        can not be edited in any way (only cloning is allowed)

        Parameter
        ---------
        node: optional, the scenario to be locked/unlocked (if not given the currently
              selected item inside the project-tree is taken)
        '''
        if not scenario_node:
            scenario_node = self.selected_item
        if scenario_node.admin_locked and not config.admin_mode:
            self.lock_button.setChecked(True)
            msgBox = QtGui.QMessageBox()
            msgBox.setWindowTitle(_fromUtf8('Warnung'))
            msgBox.setText(_fromUtf8('Das Szenario wurde durch den Admin ' +
                                     'gesperrt und kann nur durch ihn ' +
                                     'entsperrt oder bearbeitet werden.'))
            msgBox.exec_()
            return
        scenario_node.locked = not scenario_node.locked
        if config.admin_mode:
            scenario_node.admin_locked = scenario_node.locked
        self.project_changed.emit()

    def _rename_node(self, node=None):
        '''
        rename a node of the project-tree, opens a dialog to ask for a new name

        Parameter
        ---------
        node: optional, the node to be renamed (if not given the currently
              selected item inside the project-tree is taken)
        '''
        if not node:
            node = self.selected_item
        name, ok = QtGui.QInputDialog.getText(
            None, 'Umbenennen', 'Neuen Namen eingeben:',
            QtGui.QLineEdit.Normal, node.name)
        if ok:
            node.name = str(name)
            self.project_changed.emit()

    def _rename_scenario(self, scenario_node=None):
        '''
        rename the scenario by asking the user for a new name.
        tries to rename the path as well.

        Parameter
        ---------
        scenario_node: optional, the scenario to be renamed (if not given the currently
                       selected item inside the project-tree is taken)
        '''
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
                old_name = scenario_node.name
                scenario_node.name = str(name)
                try:
                    os.rename(old_path, scenario_node.path)
                except Exception, e:
                    scenario_node.name = old_name
                    QtGui.QMessageBox.about(
                        None, 'Fehler',
                        _fromUtf8('Das Szenario konnte nicht umbenannt werden: \n'+
                                  str(e)))
                self.project_changed.emit()
                break
            else:
                break

    def _copy_special_run(self, output_node=None):
        '''
        copy an output-node (representing a special run) to another (or even the
        same) scenario. Opens dialog to ask for the new name of the clone and the
        target-scenario

        Parameter
        ---------
        output_node: optional, the node to be copied (if not given the currently selected
                     item inside the project-tree is taken)
        '''
        if not output_node:
            output_node = self.selected_item
        if output_node.is_primary:
            QtGui.QMessageBox.about(
                None, 'Fehler',
                _fromUtf8('Gesamtläufe können nicht kopiert werden.'))
            return
        new_name, scenario_name, ok = CopySpecialRunDialog.getValues(output_node)
        if ok:
            scenario = self.project.get_child(scenario_name)
            new_run = scenario.add_run(new_name, output_node.options)

    def clone_scenario(self, scenario_node=None, do_choose=False,
                       new_scenario_name=None):
        '''
        clone a scenario including all of it's resources. the resources will be
        hard copied to a new scenario-folder inside project-folder (progress
        is shown in seperate dialog)

        Parameter
        ---------
        scenario_node:     optional, the node of the scenario to be cloned(if not given
                           the currently selected item inside the project-tree
                           is taken)
        do_choose:         optional, if True, user has to select scenario in a dialog
        new_scenario_name: optional, the name the clone will get (opens dialog to ask
                           user for it, if not given)
        '''
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
                _fromUtf8('Der Pfad "{}" existiert bereits. '.format(path) +
                          'Wollen Sie trotzdem fortsetzen?'),
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

    def open_resource(self, resource_node=None):
        '''
        open the a resource-file with hdf5-viewer defined in configuration

        Parameter
        ---------
        resource_node: optional, the node linking the resource to be opened(if not given
                       the currently selected item inside the project-tree is taken)
        '''
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
        '''
        add a new scenario to the currently opened project, opens dialogs to
        ask for a name and if defaults shall be used
        '''
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
        add a run to a scenario.
        adds primary run, if none is existing yet, adds special run else.
        calls dialogs to choose options, name and asks to start run right away

        Parameter
        ---------
        scenario: optional, scenario node, where run should be added(if not given
                  the currently selected item inside the project-tree is taken)
        do_choose: optional, open dialog to let user choose scenario manually

        Return
        ---------
        run-node, that was added,
        None, if no run could be created
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
        '''
        add a primary run to a scenario. calls dialogs to choose options, name
        and asks to start run right away

        Parameter
        ---------
        scenario: optional, scenario node, where primary run should be added(if not given
                  the currently selected item inside the project-tree is taken)
        do_choose: optional, open dialog to let user choose scenario manually

        Return
        ---------
        run-node, that was added,
        None, if no run could be created
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
            run_node = scenario.get_output(Scenario.PRIMARY_RUN)
            self.select_node(run_node)
            return

        options, ok = RunOptionsDialog.getValues(scenario, is_primary=True)
        if not ok:
            return
        run_node = scenario.add_run(Scenario.PRIMARY_RUN, options)
        run_node.is_valid = False
        self.select_node(run_node)
        reply = QtGui.QMessageBox.question(
            None, _fromUtf8('Ausführung'),
            _fromUtf8('Soll der angelegte Gesamtlauf jetzt durchgeführt werden?'),
            QtGui.QMessageBox.Yes, QtGui.QMessageBox.Cancel)
        if reply == QtGui.QMessageBox.Yes:
            self.run(scenario, run_name=run_node.name, options=run_node.options)
        self.nodes_changed.emit(run_node)
        return run_node

    def add_special_run(self, scenario=None, do_choose=False):
        '''
        add a special run to a scenario. calls dialogs to choose options, name
        and asks to start run right away

        Parameter
        ---------
        scenario: optional, scenario node, where special run should be added (if not given
                  the currently selected item inside the project-tree is taken)
        do_choose: optional, open dialog to let user choose scenario manually

        Return
        ---------
        run-node, that was added,
        None, if no run could be created
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

        default = 'spezifischer Lauf {}'.format(
            len(scenario.get_output_files()) - 1)
        run_name, ok = InputDialog.getValues(_fromUtf8(
            'Name für den spezifischen Lauf'), default)
        if ok:
            options, ok = RunOptionsDialog.getValues(scenario, is_primary = False)
            if ok:
                run_node = scenario.add_run(run_name, options=options)
                run_node.is_valid = False
                self.select_node(run_node)
                reply = QtGui.QMessageBox.question(
                    None, _fromUtf8('Ausführung'),
                    _fromUtf8('Soll der angelegte Lauf jetzt durchgeführt werden?'),
                    QtGui.QMessageBox.Yes, QtGui.QMessageBox.Cancel)
                if reply == QtGui.QMessageBox.Yes:
                    self.run(scenario, run_name=run_node.name, options=run_node.options)
                self.nodes_changed.emit(run_node)
                return run_node


    def _reset_scenario(self, scenario_node=None, ask_overwrite=True):
        '''
        reset all resources of a scenario to their defaults by copying all
        files from the default folder to the project/scenario folder and
        link the project-tree to those files

        Parameter
        ---------
        scenario:      optional, scenario node, that shall be reset(if not given the
                       currently selected item inside the project-tree is taken)
        ask_overwrite: optional, if True, existing files are overwritten without
                       asking for permission
        '''
        if not scenario_node:
            scenario_node = self.selected_item

        if ask_overwrite:
            reply = QtGui.QMessageBox.question(
                        None, _fromUtf8("Zurücksetzen"),
                        _fromUtf8('Soll das gesamte Szenario "{}" '
                                  .format(scenario_node.name) +
                                  'inklusive der Ein- und Ausgaben auf die ' +
                                  'Standardwerte zurückgesetzt werden?'),
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

        self.nodes_changed.emit(scenario_node)

    def _reset_resource(self, res_node=None):
        '''
        reset a resource node to it's default by copying the file from the
        default folder to the resource-folder and linking this file

        Parameter
        ---------
        res_node: optional, the node linking the resource to be reset, if not given, the
                  currently selected item inside the project-tree is taken
        '''
        if not res_node:
            res_node = self.selected_item

        scenario = res_node.scenario
        if len(scenario.get_output_files()) > 0:
            reply = QtGui.QMessageBox.question(
                None, _fromUtf8("Zurücksetzen"),
                _fromUtf8('Wenn Sie die Ressource zurücksetzen, werden alle ' +
                          'bestehenden Ausgaben ungültig und somit entfernt!'),
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
            self.nodes_changed.emit(scenario)

    def write_project(self, filename):
        '''
        write the current state of the opened project to disk (containing
        structure of project-tree and links to resource-files)

        Parameter
        ---------
        filename: the xml-file that the project will be stored in
        '''
        XMLParser.write_xml(self.project, filename)

    def new_project(self, name, project_folder):
        '''
        write the current state of the opened project to disk (containing
        structure of project-tree and links to resource-files)

        Parameter
        ---------
        name:           the name of the project to be created
        project_folder: the folder, the project-file will be created in
                       (all resources will be stored in subfolders of this
                        folder!)

        Return
        ---------
        boolean: True, if project was successfully created, else False
        '''
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
        self.project.on_change(lambda: self.project_changed.emit())
        index = self.createIndex(0, 0, self.project)
        self.select_item(index)
        self.tree_view.setCurrentIndex(index)
        return True

    def close_project(self):
        '''
        close the currently opened project
        '''
        self.current_index = self.createIndex(0, 0, self.project)
        if self.project:
            self._remove_node(self.project)
        self.view_changed.emit()

    def read_project(self, filename):
        '''
        read a project from an xml-file

        Parameter
        ---------
        filename: the project-file (xml) that the contains the structure of
        the project-tree and the links to the resource-files
        '''
        self.close_project()
        XMLParser.read_xml(self.model, filename)
        self.project.on_change(lambda: self.project_changed.emit())
        self.project.project_folder = os.path.split(filename)[0]
        self.project.update()
        self.nodes_changed.emit(self.project)
        self.view_changed.emit()
        self.tree_view.resizeColumnToContents(0)
        self.select_node(self.project)

    def remove_outputs(self, scenario):
        '''
        remove all output-nodes of the scenario from the project-tree and
        remove the linked files from disk

        Parameter
        ---------
        scenario: the scenario, where the outputs shall be removed
        '''
        for output_node in scenario.get_output_files():
            try:
                rmtree(os.path.split(output_node.file_absolute)[0])
            except:
                pass
        output_parent = scenario.get_child(scenario.OUTPUT_NODES)
        if output_parent:
            self._remove_node(output_parent)

    def validate_nodes(self, *args):
        '''
        handle what happens, if nodes have changed
        '''
        for node in args:
            # if input changes, all other nodes have to be validated
            if isinstance(node, InputNode):
                scenario = node.scenario
                scenario.validate()
            else:
                node.validate()