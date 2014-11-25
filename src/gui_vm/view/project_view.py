# -*- coding: utf-8 -*-
from PyQt4 import (QtCore, QtGui)
from details import (SimRunDetails, ProjectDetails, ResourceDetails)
from gui_vm.model.project_tree import (Project, ProjectTreeNode, SimRun,
                                       ResourceNode, XMLParser)
from gui_vm.view.dialogs import (CopyFilesDialog, ExecDialog,
                                 NewSimRunDialog)
from gui_vm.config.config import Config
import os

config = Config()
config.read()

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

class ProjectTreeView(QtCore.QAbstractItemModel):
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
    refreshable = QtCore.pyqtSignal(bool)
    executable = QtCore.pyqtSignal(bool)
    reloadable = QtCore.pyqtSignal(bool)

    def __init__(self, parent=None):
        super(ProjectTreeView, self).__init__()
        self.parent_dialog = parent
        self.root = ProjectTreeNode('root')
        self.header = ('Projektbrowser', 'Details')
        self.count = 0
        self.details = None
        self.current_index = None

    @property
    def selected_item(self):
        return self.nodeFromIndex(self.current_index)

    @property
    def project(self):
        return self.root.child_at_row(0)

    def add(self):
        node = self.selected_item
        if isinstance(node, Project):
            self.add_run()
        elif isinstance(node, SimRun):
            self.add_run()

    def remove(self, node=None):
        if not isinstance(node, ProjectTreeNode):
            node = self.selected_item
        if isinstance(node, SimRun):
            parent_idx = self.parent(self.current_index)
            self.remove_row(self.current_index.row(),
                            parent_idx)
            self.remove_run(node)
            self.item_clicked(parent_idx)
        elif isinstance(node, Project):
            project_node = node
            self.remove_row(self.current_index.row(),
                            self.parent(self.current_index))
            self.item_clicked(self.createIndex(0, 0))
            return
        elif isinstance(node, ResourceNode):
            self.remove_resource(node)
        self.project_changed.emit()

    def edit(self):
        node = self.selected_item
        if node.rename:
            text, ok = QtGui.QInputDialog.getText(
                None, 'Umbenennen', 'Neuen Namen eingeben:',
                QtGui.QLineEdit.Normal, node.name)
            if ok:
                node.name = str(text)
                self.project_changed.emit()

    def reset(self):
        node = self.selected_item
        if isinstance(node, SimRun):
            self.reset_simrun()
        elif isinstance(node, ResourceNode):
            self.reset_resource()

    def run(self):
        node = self.selected_item
        if isinstance(node, SimRun):
            dialog = ExecDialog(node, parent=self.parent_dialog)

    def do_reload(self):
        node = self.selected_item
        node.validate()
        self.view_changed.emit()

    def add_run(self):
        project = self.project
        if (not project):
            return
        default_name = 'Szenario {}'.format(project.child_count)
        simrun_name, model_name, ok = NewSimRunDialog.getValues(default_name)
        if ok:
            if simrun_name in project.children_names:
                QtGui.QMessageBox.about(
                    None, "Fehler",
                    _fromUtf8("Der Szenarioname '{}' ist bereits vergeben."
                              .format(simrun_name)))
            else:
                project.add_run(model=model_name, name=simrun_name)
                reply = QtGui.QMessageBox.question(
                    None, _fromUtf8("Neues Szenario erstellen"),
                    _fromUtf8("Möchten Sie die Standarddateien " +
                              "für das neue Szenario verwenden?"),
                    QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
                do_copy = reply == QtGui.QMessageBox.Yes
                if do_copy:
                    self.reset_simrun(
                        simrun_node=project.get_child(simrun_name))
                self.project_changed.emit()

    def remove_run(self, simrun_node):
        self.project.remove_run(simrun_node.name)

    def remove_project(self, project_node):
        project_node.remove()

    def remove_resource(self, resource_node):
        '''
        remove the source of the resource node and optionally remove it from
        the disk
        '''
        if os.path.exists(resource_node.full_source):
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

    def reset_simrun(self, simrun_node=None):
        '''
        set the simrun to default, copy all files from the default folder
        to the project/scenario folder and link the project tree to those
        files
        '''
        #self.project_tree_view.reset(self.row_index)
        if simrun_node is None:
            simrun_node = self.selected_item
        simrun_node = simrun_node.reset_to_default()
        filenames = []
        destinations = []
        for res_node in simrun_node.get_resources():
            filenames.append(res_node.original_source)
            destinations.append(os.path.join(res_node.full_path))

        #bad workaround (as it has to know the parents qtreeview)
        #but the view crashes otherwise, maybe make update signal
        self.parent_dialog.qtreeview.setUpdatesEnabled(False)
        dialog = CopyFilesDialog(filenames, destinations,
                                 parent=self.parent_dialog)
        self.parent_dialog.qtreeview.setUpdatesEnabled(True)
        #dialog.deleteLater()
        simrun_node.update()
        self.project_changed.emit()

    def reset_resource(self):
        res_node = self.selected_item
        res_node.reset_to_default()
        filename = res_node.original_source
        destination = res_node.full_path
        dialog = CopyFilesDialog(filename, destination,
                                 parent=self.parent_dialog)
        res_node.update()
        self.project_changed.emit()

    def write_project(self, filename):
        XMLParser.write_xml(self.project, filename)

    def create_project(self, name, project_folder):
        if name is None:
            name = 'Neues Projekt'
        if self.project:
            self.remove(self.project)
            self.remove_row(self.current_index.row(),
                            self.parent(self.current_index))
        self.root.add_child(Project(name, project_folder=project_folder))
        self.item_clicked(self.createIndex(0, 0, self.project))

    def read_project(self, filename):
        self.current_index = self.createIndex(0, 0, self.project)
        if self.project:
            self.remove(self.project)
        self.root = XMLParser.read_xml(self.root, filename)
        self.project.project_folder = os.path.split(filename)[0]
        self.project.update()
        self.view_changed.emit()

    def item_clicked(self, index=None):
        '''
        show details when row of project tree is clicked
        details shown depend on type of node that is behind the clicked row
        '''
        self.current_index = index
        node = self.selected_item
        #def do_nothing(*args): pass

        #clear the old details
        if self.details:
            self.details.close()
            self.details = None

        if node and node.rename:
            self.editable.emit(True)
        else:
            self.editable.emit(False)

        if isinstance(node, Project):
            self.addable.emit(True)
            #self.add = self.add_run
            self.removable.emit(False)
            #self.remove = do_nothing
            self.resetable.emit(False)
            #self.reset = do_nothing
            self.refreshable.emit(True)
            #self.refresh = do_nothing
            self.executable.emit(False)
            self.reloadable.emit(False)
            self.details = ProjectDetails(node)

        elif isinstance(node, SimRun):
            self.addable.emit(True)
            self.removable.emit(True)
            self.resetable.emit(True)
            self.refreshable.emit(True)
            self.executable.emit(True)
            self.reloadable.emit(True)
            self.details = SimRunDetails(node)

        elif isinstance(node, ResourceNode):
            self.addable.emit(False)
            self.removable.emit(True)
            self.resetable.emit(True)
            self.refreshable.emit(True)
            self.executable.emit(False)
            self.reloadable.emit(True)
            self.details = ResourceDetails(node)

        else:
            self.addable.emit(False)
            self.removable.emit(False)
            self.resetable.emit(False)
            self.refreshable.emit(False)
            self.executable.emit(False)
            self.reloadable.emit(False)

        if self.details:
            self.details.value_changed.connect(self.project_changed)
        self.dataChanged.emit(index, index)

    def refresh_details(self):

        node = self.selected_item
        if self.details:
            self.details.close()
            self.details = self.details.__class__(node)
            self.details.value_changed.connect(self.project_changed)

    def replace(self, index, new_node):
        pass

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
            if (isinstance(node, SimRun) or isinstance(node, Project)):
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

        if node is None or not isinstance(node, ProjectTreeNode):
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
        return index.internalPointer() if index.isValid() else self.root

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
        menu = QtGui.QMenu()
        hallo = menu.addAction("Hallo")
        huhu = menu.addAction("Huhu")
        quitAction = menu.addAction("Quit")
        action = menu.exec_(self.parent_dialog.mapToGlobal(pos))
        if action == quitAction:
            pass  #qApp.quit()