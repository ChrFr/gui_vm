import sys
from main_window_ui import Ui_MainWindow
from PyQt4 import QtGui, QtCore
from project_view import ProjectTreeModel
from resource_ui import Ui_DetailsResource
from simrun_ui import Ui_DetailsSimRun
from project_ui import Ui_DetailsProject
from config import DEFAULT_FOLDER
import os

class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
    project_changed = QtCore.pyqtSignal()

    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.setupUi(self)
        self.project_tree = ProjectTreeModel()
        self.project_tree_view.setModel(self.project_tree)
        #self.project_tree_view.expandAll()
        self.refresh_view()
        self.details = None

        #connect the buttons
        self.plus_button.clicked.connect(self.add_run)
        self.plus_button.clicked.connect(self.refresh_view)
        self.save_button.clicked.connect(self.save_project)

        #connect the tool bar
        self.actionProjekt_speichern.triggered.connect(self.save_project)
        self.actionProjekt_ffnen.triggered.connect(self.load_project)
        self.actionNeues_Projekt.triggered.connect(self.create_project)
        self.actionBeenden.triggered.connect(QtGui.qApp.quit)

        self.row_index = 0
        self.project_tree_view.clicked[QtCore.QModelIndex].connect(
            self.row_clicked)
        self.project_tree.dataChanged.connect(self.refresh_view)
        self.project_changed.connect(self.refresh_view)

    def add_run(self):
        self.project_tree.add_run()

    def create_project(self):
        '''
        create a new project
        '''
        text, ok = QtGui.QInputDialog.getText(
            self, 'Neues Projekt', 'Name des neuen Projekts:',
            QtGui.QLineEdit.Normal, 'Neues Projekt')
        if ok:
            name = str(text)
            self.project_tree = ProjectTreeModel(name=name)
            self.project_tree_view.setModel(self.project_tree)
            self.refresh_view()
            self.project_tree.dataChanged.connect(self.refresh_view)

    def load_project(self):
        '''
        load a project
        '''
        fileinput = str(QtGui.QFileDialog.getOpenFileName(
            self, 'Projekt öffnen', '.', '*.xml'))
        if len(fileinput) > 0:
            self.project_tree.read_project(fileinput)
            self.refresh_view()
            #self.project_tree_view.setModel(self.project_tree)

    def save_project(self):
        '''
        save the project
        '''
        filename = str(QtGui.QFileDialog.getSaveFileName(
            self, 'Projekt speichern', '.', '*.xml'))
        #filename is '' if aborted
        if len(filename) > 0:
            #get first project (by now only 1 project is displayed)
            #need to change, if there are more
            self.project_tree.write_project(
                self.project_tree.root.child_at_row(0).name, filename)
            QtGui.QMessageBox.about(
                self, "Speichern erfolgreich",
                'Die Speicherung des Projektes\n{}\n war erfolgreich'.
                format(filename))

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
            #rename node if allowed
            if node.rename:
                text, ok = QtGui.QInputDialog.getText(
                    self, 'Umbenennen', 'Neuen Namen eingeben:',
                    QtGui.QLineEdit.Normal, node.name)
                if ok:
                    node.name = str(text)
                    self.project_changed.emit()
        #clicked another row
        else:
            self.row_index = index
            #clear the old details
            if self.details:
                self.details.close()
            #show details depending on type of node
            if node.__class__.__name__ == 'Project':
                self.details = ProjectDetails(node, self.details_layout)
            elif node.__class__.__name__ == 'SimRun':
                self.details = SimRunDetails(node, self.details_layout)
            elif node.__class__.__name__ == 'ResourceNode':
                self.details = ResourceDetails(node, self.details_layout)
            if self.details:
                self.details.value_changed.connect(self.refresh_view)


class SimRunDetails(QtGui.QGroupBox, Ui_DetailsSimRun):
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

    def __init__(self, node, parent):
        super(SimRunDetails, self).__init__()
        self.setupUi(self)
        self.parent = parent
        self.parent.addWidget(self)
        self.setTitle(node.name)
        self.node = node
        self.combo_model.addItems(self.node._available)
        index = self.combo_model.findText(self.node.model.name)
        self.combo_model.setCurrentIndex(index)
        self.combo_model.currentIndexChanged['QString'].connect(self.changeModel)
        self.show()

    def changeModel(self, name):
        self.node.set_model(str(name))
        self.value_changed.emit()

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

    def __init__(self, node, parent):
        super(ProjectDetails, self).__init__()
        self.setupUi(self)
        self.node = node
        self.parent = parent
        self.parent.addWidget(self)
        self.setTitle(node.name)
        for meta in node.meta:
            label = QtGui.QLabel(meta)
            edit = QtGui.QLineEdit(node.meta[meta])
            edit.setReadOnly(True)
            self.meta_layout.addRow(label, edit)
        self.folder_edit.setText(self.node.project_folder)

        self.folder_browse_button.clicked.connect(self.browse_folder)
        self.folder_edit.textChanged.connect(self.update)
        self.show()

    def update(self):
        self.node.project_folder = (str(self.folder_edit.text()))
        self.value_changed.emit()

    def browse_folder(self):
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

    def __init__(self, node, parent):
        super(ResourceDetails, self).__init__()
        self.setupUi(self)
        self.parent = parent
        self.parent.addWidget(self)
        self.node = node
        self.project_copy.setText(self.node.source)
        self.file_edit.setText(self.node.original_source)
        self.setTitle(node.name)
        self.browse_button.clicked.connect(self.browse_files)
        self.file_edit.textChanged.connect(self.update)
        attr = self.node.resource.attributes
        self.attribute_view.setColumnCount(3)
        self.attribute_view.setRowCount(len(attr))
        for i, key in enumerate(attr):
            self.attribute_view.setItem(
                i, 0, QtGui.QTableWidgetItem(key))
            self.attribute_view.setItem(
                i, 1, QtGui.QTableWidgetItem(attr[key]))
        header = self.attribute_view.horizontalHeader()
        header.setResizeMode(QtGui.QHeaderView.Stretch)
        labels = ['Komponente', 'Attribute', 'Status']
        self.attribute_view.setHorizontalHeaderLabels(labels)
        self.show()

    def browse_files(self):
        fileinput = str(
            QtGui.QFileDialog.getOpenFileName(
                self, 'Ressourcenatei öffnen', '.'))
        #filename is '' if aborted
        if len(fileinput) > 0:
            self.file_edit.setText(fileinput)

    def update(self):
        self.node.set_source(str(self.file_edit.text()))
        self.value_changed.emit()

    def __del__(self):
        pass

def startmain():
    app = QtGui.QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    startmain()