from PyQt4 import (QtCore, QtGui)
from gui_vm.model.project_tree import (Project, ProjectTreeNode,
                                                XMLParser)


class ProjectTreeModel(QtCore.QAbstractItemModel):
    def __init__(self, parent=None):
        super(ProjectTreeModel, self).__init__(parent)
        self.root = ProjectTreeNode('root')
        self.header = ('Projektbrowser', 'Details')

    @property
    def project(self):
        return self.root.child_at_row(0)

    def add_run(self, model):
        self.project.add_run(model)

    #def flags(self, index):
        #defaultFlags = QAbstractItemModel.flags(self, index)

        #if index.isValid():
            #return Qt.ItemIsEditable | Qt.ItemIsDragEnabled | \
                    #Qt.ItemIsDropEnabled | defaultFlags

        #else:
            #return Qt.ItemIsDropEnabled | defaultFlags

    def write_project(self, filename):
        XMLParser.write_xml(self.project, filename)

    def create_project(self, name):
        if name is None:
            name = 'Neues Projekt'
        self.root.add_child(Project(name))

    def read_project(self, filename):
        self.root = XMLParser.read_xml('root', filename)

    #def get_details(self, index):
        #node = self.model().data(index, QtCore.Qt.UserRole)

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
        return node.child_count()

    def parent(self, child):
        if not child.isValid():
            return QModelIndex()

        node = self.nodeFromIndex(child)

        if node is None:
            return QModelIndex()

        parent = node.parent

        if parent is None:
            return QModelIndex()

        grandparent = parent.parent
        if grandparent is None:
            return QtCore.QModelIndex()
        row = grandparent.row_of_child(parent)

        assert row != - 1
        return self.createIndex(row, 0, parent)

    def nodeFromIndex(self, index):
        return index.internalPointer() if index.isValid() else self.root


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


    #def insertRow(self, row, parent):
        #return self.insertRows(row, 1, parent)


    #def insertRows(self, row, count, parent):
        #self.beginInsertRows(parent, row, (row + (count - 1)))
        #self.endInsertRows()
        #return True


    #def remove_row(self, row, parentIndex):
        #return self.removeRows(row, 1, parentIndex)


    #def removeRows(self, row, count, parentIndex):
        #self.beginRemoveRows(parentIndex, row, row)
        #node = self.nodeFromIndex(parentIndex)
        #node.removeChild(row)
        #self.endRemoveRows()

        #return True
