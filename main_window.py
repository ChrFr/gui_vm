import sys
from main_window_ui import Ui_MainWindow
from PyQt4 import QtGui, QtCore
from project_view import ProjectTreeModel

class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.setupUi(self)
        self.project_tree = ProjectTreeModel()
        self.project_tree_view.setModel(self.project_tree)
        self.project_tree_view.expandAll()
        self.details = Details(None, self.info_layout)
        #Slots for the plus and minus buttons
        self.plus_button.clicked.connect(self.project_tree.add_run)
        self.plus_button.clicked.connect(self.refresh_view)
        self.row_index = 0
        self.project_tree_view.clicked[QtCore.QModelIndex].connect(
            self.row_clicked)
        self.project_tree.dataChanged.connect(self.refresh_view)

    def refresh_view(self):
        '''
        refresh the view on the project tree
        '''
        self.project_tree_view.expandAll()
        for column in range(self.project_tree_view.model()
                            .columnCount(QtCore.QModelIndex())):
            self.project_tree_view.resizeColumnToContents(column)

    def row_clicked(self, index):
        '''
        show details when row of project tree is clicked
        details shown depend on type of node that is behind the clicked row
        '''
        node = self.project_tree_view.model().data(index, QtCore.Qt.UserRole)
        #clicked highlighted row
        if self.row_index == index:
            print node.rename
        #clicked another row
        else:
            self.row_index = index
            #clear the old details
            clear_layout(self.info_layout)
            if node.__class__.__name__ == 'Project':
                self.details = ProjectDetails(node, self.info_layout)
            elif node.__class__.__name__ == 'SimRun':
                self.details = SimRunDetails(node, self.info_layout)
            elif node.__class__.__name__ == 'ResourceNode':
                self.details = ResourceDetails(node, self.info_layout)


class Details(QtGui.QWidget):
    '''
    base class for the details of nodes, shown in a given layout

    Parameters
    ----------
    node: Node of the project tree
    parent: layout the details will be added to
    '''
    def __init__(self, node, parent):
        QtGui.QVBoxLayout.__init__(self)
        self.node = node
        self.parent = parent
        self.parent.addWidget(self)

    def __del__(self):
        pass
        #clear_layout(self.parent)

def clear_layout(layout):
    '''
    remove all child widgets of the given layout

    Parameters
    ----------
    layout: QVBoxLayout,
            layout whose child widgets are removed
    '''
    for i in reversed(range(layout.count())):
        item = layout.itemAt(i)
        if isinstance(item, QtGui.QWidgetItem):
            item.widget().close()
        else:
            clear_layout(item.layout())
        layout.removeItem(item)


class SimRunDetails(Details):
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
    def __init__(self, node, parent):
        super(SimRunDetails, self).__init__(node, parent)
        self.form = QtGui.QFormLayout()
        self.label = QtGui.QLabel('Verkehrsmodell')
        self.combo = QtGui.QComboBox()
        self.combo.setEditable(True)
        self.combo.addItems(self.node._available)
        self.combo.currentIndexChanged['QString'].connect(self.changeModel)
        self.form.addRow(self.label, self.combo)
        self.parent.addLayout(self.form)

    def changeModel(self, name):
        self.node.set_model(name)

class ProjectDetails(Details):
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
    def __init__(self, node, parent):
        super(ProjectDetails, self).__init__(node, parent)
        self.form = QtGui.QFormLayout()
        for meta in node.meta:
            label = QtGui.QLabel(meta)
            edit = QtGui.QLineEdit(node.meta[meta])
            edit.setReadOnly(True)
            self.form.addRow(label, edit)
        self.addLayout(self.form)


class ResourceDetails(Details):
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
    def __init__(self, node, parent):
        super(ResourceDetails, self).__init__(node, parent)
        self.form = QtGui.QFormLayout()
        label = QtGui.QLabel('Datei')
        edit = QtGui.QLineEdit(self.node.source)
        self.browse_button = QtGui.QPushButton('...')
        self.browse_button.clicked.connect(self.browse_files)
        self.form.addRow(label)
        self.form.addRow(edit, self.browse_button)
        self.parent.addLayout(self.form)

    def browse_files(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, 'Open File', '.')
        print filename

def startmain():
    app = QtGui.QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    startmain()