# -*- coding: utf-8 -*-
'''
determine how to react on user input, layer between gui and the project
'''

from PyQt4 import (QtCore, QtGui)
from details import (SimRunDetails, ProjectDetails, ResourceDetails)
from gui_vm.model.project_tree import (Project, ProjectTreeNode, SimRun,
                                       ResourceNode, XMLParser)
import sys


class ProjectTreeControl(QtCore.QAbstractItemModel):
    details_changed = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(ProjectTreeControl, self).__init__(parent)
        self.root = ProjectTreeNode('root')
        self.header = ('Projektbrowser', 'Details')
        self.count = 0
        self.details = None

    @property
    def project(self):
        return self.root.child_at_row(0)

    def add_run(self, model):
        self.project.add_run(model)

    def write_project(self, filename):
        XMLParser.write_xml(self.project, filename)

    def create_project(self, name):
        if name is None:
            name = 'Neues Projekt'
        self.root.add_child(Project(name))

    def read_project(self, filename):
        self.root = XMLParser.read_xml('root', filename)


    def row_changed(self, index):
        '''
        show details when row of project tree is clicked
        details shown depend on type of node that is behind the clicked row
        '''
        node = self.nodeFromIndex(index)
        #clicked highlighted row
        #if self.row_index == index:
            ##rename node if allowed
            #self.rename()
        ##clicked another row
        #else:
        self.row_index = index
        #clear the old details
        if self.details:
            self.details.close()
            self.details = None
        #reset all context dependent buttons
        #self.button_group_label.setText('')
        #for button in self.context_button_group.children():
            #button.setEnabled(False)
            #button.setToolTip('')
            #try:
                #button.clicked.disconnect()
            #except:
                #pass

        #if node.rename:
            #self.edit_button.setEnabled(True)
            #self.edit_button.clicked.connect(self.rename)
            #self.edit_button.setToolTip('Umbenennen')

        #show details and set buttons depending on type of node
        if isinstance(node, Project):
            #self.button_group_label.setText('Projekt bearbeiten')

            #self.plus_button.setEnabled(True)
            #self.plus_button.setToolTip(_fromUtf8('Szenario hinzufügen'))
            #self.plus_button.clicked.connect(self.add_run)

            self.details = ProjectDetails(node)

        elif isinstance(node, SimRun):
            #self.button_group_label.setText('Szenario bearbeiten')

            #self.minus_button.setEnabled(True)
            #self.minus_button.setToolTip(_fromUtf8('Szenario löschen'))
            #self.minus_button.clicked.connect(self.remove_run)

            #self.plus_button.setEnabled(True)
            #self.plus_button.setToolTip(_fromUtf8('Szenario hinzufügen'))
            #self.plus_button.clicked.connect(self.add_run)

            #self.reset_button.setEnabled(True)
            #self.reset_button.clicked.connect(self.reset_simrun)
            #self.reset_button.setToolTip(
                #_fromUtf8('Default wiederherstellen'))

            self.details = SimRunDetails(node)

        elif isinstance(node, ResourceNode):
            #self.button_group_label.setText('Ressource bearbeiten')

            #self.minus_button.setEnabled(True)
            #self.minus_button.setToolTip(_fromUtf8('Ressource löschen'))
            #self.minus_button.clicked.connect(self.remove_resource)

            #self.reset_button.setEnabled(True)
            #self.reset_button.clicked.connect(self.reset_resource)
            #self.reset_button.setToolTip(
                #_fromUtf8('Default wiederherstellen'))

            self.details = ResourceDetails(node)

        if self.details:
            self.details.value_changed.connect(self.details_changed)
        self.dataChanged.emit(index, index)

    def replace(self, index, new_node):
        pass

    def headerData(self, section, orientation, role):
        if (orientation == QtCore.Qt.Horizontal and
            role == QtCore.Qt.DisplayRole):
            return QtCore.QVariant(self.header[section])
        return QtCore.QVariant()

    def index(self, row, column, parent):
        node = self.nodeFromIndex(parent)
        return self.createIndex(row, column, node.child_at_row(row))


    def data(self, index, role):
        '''
        return data to the tableview depending on the requested role
        '''
        node = self.nodeFromIndex(index)
        if node is None:
            return QtCore.QVariant()
        #print '{} - {}'.format(node.name, sys.getrefcount(node))
        is_valid = True
        is_checked = False
        if hasattr(node, 'resource'):
            is_valid = node.resource.is_valid
            is_checked = node.resource.is_checked

        if role == QtCore.Qt.DecorationRole:
            return QtCore.QVariant()

        if role == QtCore.Qt.TextAlignmentRole:
            return QtCore.QVariant(
                int(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft))

        if role == QtCore.Qt.UserRole:
            return node

        #color the the 2nd column of a node depending on its status
        if role == QtCore.Qt.TextColorRole and index.column() == 1:
            if is_checked:
                if is_valid:
                    return QtCore.QVariant(QtGui.QColor(QtCore.Qt.darkGreen))
                else:
                    return QtCore.QVariant(QtGui.QColor(QtCore.Qt.red))
            else:
                return QtCore.QVariant(QtGui.QColor(QtCore.Qt.black))

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

    def parent(self, child):
        print self.count
        self.count += 1
        if not child.isValid():
            return QModelIndex()

        node = self.nodeFromIndex(child)

        if node is None or not isinstance(node, ProjectTreeNode):
            return QtCore.QModelIndex()

        parent = node.parent

        if parent is None:
            return QtCore.QModelIndex()

        grandparent = parent.parent
        if grandparent is None:
            return QtCore.QModelIndex()
        row = grandparent.row_of_child(parent)

        assert row != - 1
        return self.createIndex(row, 0, parent)

    def nodeFromIndex(self, index):
        return index.internalPointer() if index.isValid() else self.root

    #def flags(self, index):
        #defaultFlags = QAbstractItemModel.flags(self, index)

        #if index.isValid():
            #return Qt.ItemIsEditable | Qt.ItemIsDragEnabled | \
                    #Qt.ItemIsDropEnabled | defaultFlags

        #else:
            #return Qt.ItemIsDropEnabled | defaultFlags


    #def mimeTypes(self):
        #types = QStringList()
        #types.append('application/x-ets-qt4-instance')
        #return types

    #def mimeData(self, index):
        #node = self.nodeFromIndex(index[0])
        #mimeData = PyMimeData(node)
        #return mimeData


    #def dropMimeData(self, mimedata, action, row, column, parentIndex):
        #if action == Qt.IgnoreAction:
            #return True

        #dragNode = mimedata.instance()
        #parentNode = self.nodeFromIndex(parentIndex)

        ## make an copy of the node being moved
        #newNode = deepcopy(dragNode)
        #newNode.setParent(parentNode)
        #self.insertRow(len(parentNode)-1, parentIndex)
        #self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),
#parentIndex, parentIndex)
        #return True


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
        node.remove_child_at(row)
        self.endRemoveRows()

        return True
