# -*- coding: utf-8 -*-
from PyQt4 import (QtCore, QtGui)
from details import (ScenarioDetails, ProjectDetails, ResourceDetails)
from gui_vm.model.project_tree import (Project, TreeNode, Scenario,
                                       ResourceNode, XMLParser)
from gui_vm.control.dialogs import (CopyFilesDialog, ExecDialog,
                                 NewScenarioDialog)
from gui_vm.config.config import Config
import os, subprocess
from shutil import rmtree

config = Config()
config.read()

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

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
    editable = QtCore.pyqtSignal(bool)
    addable = QtCore.pyqtSignal(bool)
    removable = QtCore.pyqtSignal(bool)
    resetable = QtCore.pyqtSignal(bool)
    executable = QtCore.pyqtSignal(bool)
    lockable = QtCore.pyqtSignal(bool)
    copyable = QtCore.pyqtSignal(bool)

    def __init__(self, view=None):
        super(ProjectTreeControl, self).__init__()
        self.view = view
        self.model = None
        self.header = ('Projekt', 'Details')
        self.count = 0
        self.details = None
        self.current_index = None

    @property
    def selected_item(self):
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

        #color the the 2nd column of a node depending on its status
        if role == QtCore.Qt.TextColorRole and index.column() == 1:
            #if hasattr(node, 'is_checked'):
            is_checked = node.is_checked
            if is_checked:
                #if hasattr(node, 'is_valid'):
                is_valid = node.is_valid
                if is_valid:
                    return QtCore.QVariant(QtGui.QColor(QtCore.Qt.darkGreen))
                else:
                    return QtCore.QVariant(QtGui.QColor(QtCore.Qt.red))
            else:
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

        parent = node.parent

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
        if len(node.children) > row:
            node.remove_child_at(row)
        self.endRemoveRows()

        return True

    def pop_context_menu(self, pos):
        pass


class VMProjectControl(ProjectTreeControl):
    def __init__(self, view=None):
        super(VMProjectControl, self).__init__(view)
        self.model = TreeNode('root')

        self.context_map = {
            'add': {
                Project: [self.add_scenario, 'Szenario hinzufügen'],
                Scenario: [self.add_scenario, 'Szenario hinzufügen'],
            },
            'remove': {
                Scenario: [self._remove_scenario, 'Szenario entfernen'],
                ResourceNode: [self.remove_resource, 'Ressource entfernen'],
            },
            'reset': {
                Scenario: [self._reset_scenario, 'Szenario zurücksetzen'],
                ResourceNode: [self._reset_resource, 'Ressource zurücksetzen']
            },
            'edit': {
                Scenario: [self._rename, 'Szenario umbenennen'],
                Project: [self._rename, 'Projekt umbenennen'],
                ResourceNode: [self.edit_resource, 'Ressource editieren']
            },
            'execute': {
                Scenario: [self._run_scenario, 'Szenario starten']
            },
            'switch_lock': {
                Scenario: [self._switch_lock, 'Szenario sperren'],
            },
            'copy': {
                Scenario: [self._clone_scenario, 'Szenario klonen'],
            },
        }

    def compute_selected_node(self, function_name):
        node = self.selected_item
        cls = node.__class__
        if cls in self.context_map[function_name]:
            self.context_map[function_name][cls][0]()
        self.project_changed.emit()

    def item_clicked(self, index=None):
        '''
        show details when row of project tree is clicked
        details shown depend on type of node that is behind the clicked row
        '''
        self.current_index = index
        node = self.selected_item

        #clear the old details
        if self.details:
            self.details.close()
            self.details = None

        #get new details depending on type of node

        if isinstance(node, Project):
            self.details = ProjectDetails(node)
        elif isinstance(node, Scenario):
            self.details = ScenarioDetails(node)
        elif isinstance(node, ResourceNode):
            self.details = ResourceDetails(node, self)
        #track changes made in details
        if self.details:
            self.details.value_changed.connect(self.project_changed)

        cls = node.__class__

        #emit signal flags for context
        locked = node.locked
        self.addable.emit(cls in self.context_map['add'])
        self.removable.emit(cls in self.context_map['remove'] and not locked)
        self.resetable.emit(cls in self.context_map['reset'] and not locked)
        self.editable.emit(cls in self.context_map['edit'] and not locked)
        self.executable.emit(cls in self.context_map['execute'])
        self.lockable.emit(cls in self.context_map['switch_lock'])
        self.copyable.emit(cls in self.context_map['copy'])

        self.dataChanged.emit(index, index)

    def pop_context_menu(self, pos):
        node = self.selected_item
        if node.locked:
            return
        cls = node.__class__
        context_menu = QtGui.QMenu()
        action_map = {}
        for key, value in self.context_map.iteritems():
            if cls in value:
                action_map[context_menu.addAction(_fromUtf8(value[cls][1]))] = \
                    value[cls][0]
        action = context_menu.exec_(self.view.mapToGlobal(pos))
        context_menu.close()
        if action:
            action_map[action]()

    def update_details(self, window):
        node = self.selected_item
        if self.details:
            #self.details.close()
            #self.details = self.details.__class__(node, self)
            self.details.value_changed.connect(self.project_changed)
            window.addWidget(self.details)
            self.details.update()

    def add(self):
        self.compute_selected_node('add')

    def remove(self, node=None):
        self.compute_selected_node('remove')

    def execute(self):
        self.compute_selected_node('execute')

    def edit(self):
        self.compute_selected_node('edit')

    def reset(self):
        self.compute_selected_node('reset')

    def switch_lock(self):
        self.compute_selected_node('switch_lock')

    def copy(self):
        self.compute_selected_node('copy')

    def _remove_node(self, node):
        if not node:
            node = self.selected_item
        parent_idx = self.parent(self.current_index)
        self.remove_row(self.current_index.row(),
                        parent_idx)
        node.remove_all_children()
        self.item_clicked(parent_idx)

    def _remove_scenario(self, scenario_node=None):
        if not scenario_node:
            scenario_node = self.selected_item
        path = scenario_node.path
        reply = QtGui.QMessageBox.question(
            None, _fromUtf8("Löschen"),
            _fromUtf8("Soll das gesamte Szenario-Verzeichnis {}\n".format(
                path) + "von der Festplatte entfernt werden?"),
            QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        do_delete = reply == QtGui.QMessageBox.Yes
        if do_delete:
            try:
                rmtree(scenario_node.path)
            except Exception, e:
                QtGui.QMessageBox.about(
                None, "Fehler", str(e))
                return
        self._remove_node(scenario_node)


    def remove_resource(self, resource_node=None):
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
        full_source = resource_node.full_source
        if full_source and os.path.exists(full_source):
            reply = QtGui.QMessageBox.question(
                None, _fromUtf8("Löschen"),
                _fromUtf8("Soll die Datei {} \nin {}\n".format(
                    resource_node.resource.filename,
                    resource_node.full_path) +
                          "ebenfalls entfernt werden?"),
                QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            do_delete = reply == QtGui.QMessageBox.Yes
            if do_delete:
                os.remove(resource_node.full_source)
        resource_node.set_source(None)
        resource_node.update()
        self.project_changed.emit()

    def _run_scenario(self):
        node = self.selected_item
        dialog = ExecDialog(node, parent=self.view)

    def _switch_lock(self, resource_node=None):
        if not resource_node:
            resource_node = self.selected_item
        resource_node.locked = not resource_node.locked
        self.project_changed.emit()

    def _rename(self):
        node = self.selected_item
        text, ok = QtGui.QInputDialog.getText(
            None, 'Umbenennen', 'Neuen Namen eingeben:',
            QtGui.QLineEdit.Normal, node.name)
        if ok:
            node.name = str(text)
            self.project_changed.emit()

    def _clone_scenario(self, scenario_node=None):
        if not scenario_node:
            scenario_node = self.selected_item
        text, ok = QtGui.QInputDialog.getText(
                    None, 'Szenario kopieren', 'Name des neuen Szenarios:',
                    QtGui.QLineEdit.Normal, scenario_node.name + ' - Kopie')
        if ok:
            new_scen_name = str(text)
            if new_scen_name in self.project.children_names:
                QtGui.QMessageBox.about(
                    None, "Fehler",
                    _fromUtf8("Der Szenarioname '{}' ist bereits vergeben."
                              .format(new_scen_name)))
                return
            new_scenario_node = scenario_node.clone(new_scen_name)
            path = new_scenario_node.path
            if os.path.exists(new_scenario_node.path):
                reply = QtGui.QMessageBox.question(
                    None, _fromUtf8("Fehler"),
                    _fromUtf8("Der Pfad '{}' existiert bereits. Fortsetzen?"
                                  .format(path)),
                    QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
                if reply == QtGui.QMessageBox.No:
                    return
            scenario_node.parent.add_child(new_scenario_node)
            filenames = []
            destinations = []
            for res_node in scenario_node.get_inputs():
                new_res_node = new_scenario_node.get_input(res_node.name)
                if new_res_node:
                    filenames.append(res_node.full_source)
                    destinations.append(new_res_node.full_path)

            #bad workaround (as it has to know the parents qtreeview)
            #but the view crashes otherwise, maybe make update signal
            self.view.setUpdatesEnabled(False)
            dialog = CopyFilesDialog(filenames, destinations,
                                     parent=self.view)
            self.view.setUpdatesEnabled(True)
            scenario_node.update()
            self.project_changed.emit()

    def edit_resource(self, resource_node=None):
        if not resource_node:
            resource_node = self.selected_item
        node = self.selected_item
        hdf5_viewer = config.settings['environment']['hdf5_viewer']
        if hdf5_viewer:
            subprocess.Popen('"{0}" "{1}"'.format(hdf5_viewer,
                                                  node.full_source))

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
                reply = QtGui.QMessageBox.question(
                    None, _fromUtf8("Neues Szenario erstellen"),
                    _fromUtf8("Möchten Sie die Standarddateien " +
                              "für das neue Szenario verwenden?"),
                    QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
                do_copy = reply == QtGui.QMessageBox.Yes
                if do_copy:
                    self._reset_scenario(
                        scenario_node=project.get_child(scenario_name))
                self.project_changed.emit()

    def _reset_scenario(self, scenario_node=None):
        '''
        set the simrun to default, copy all files from the default folder
        to the project/scenario folder and link the project tree to those
        files
        '''
        #self.project_tree_view.reset(self.row_index)
        if not scenario_node:
            scenario_node = self.selected_item
        scenario_node = scenario_node.reset_to_default()

        if not scenario_node:
            QtGui.QMessageBox.about(
                None, "Fehler",
                _fromUtf8("Die Defaults des Modells " +
                          "konnten nicht geladen werden."))
        else:
            filenames = []
            destinations = []
            for res_node in scenario_node.get_inputs():
                filenames.append(res_node.original_source)
                destinations.append(res_node.full_path)

            #bad workaround (as it has to know the parents qtreeview)
            #but the view crashes otherwise, maybe make update signal
            self.view.setUpdatesEnabled(False)
            dialog = CopyFilesDialog(filenames, destinations,
                                     parent=self.view)
            self.view.setUpdatesEnabled(True)
            #dialog.deleteLater()
            scenario_node.update()

        self.project_changed.emit()

    def validate_project(self):
        scenarios = self.project.find_all_by_class(Scenario)
        for scen in scenarios:
            scen.validate()
        self.view_changed.emit()

    def _reset_resource(self):
        res_node = self.selected_item
        res_node.reset_to_default()
        filename = res_node.original_source
        destination = res_node.full_path
        dialog = CopyFilesDialog(filename, destination,
                                 parent=self.view)
        res_node.update()
        self.project_changed.emit()

    def write_project(self, filename):
        XMLParser.write_xml(self.project, filename)

    def new_project(self, name, project_folder):
        if name is None:
            name = 'Neues Projekt'
        if self.project:
            self.remove(self.project)
            self.remove_row(self.current_index.row(),
                            self.parent(self.current_index))
        self.model.add_child(Project(name, project_folder=project_folder))
        self.project.on_change(self.project_changed.emit)
        self.item_clicked(self.createIndex(0, 0, self.project))

    def read_project(self, filename):
        self.current_index = self.createIndex(0, 0, self.project)
        if self.project:
            self.remove(self.project)
            self.remove_row(self.current_index.row(),
                            self.parent(self.current_index))
        self.model = XMLParser.read_xml(self.model, filename)
        self.project.on_change(self.project_changed.emit)
        self.project.project_folder = os.path.split(filename)[0]
        self.project.update()
        self.project_changed.emit()
        self.view_changed.emit()
