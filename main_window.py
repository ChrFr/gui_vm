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

        #Slots for the plus and minus buttons
        self.plus_button.clicked.connect(self.project_tree.add_run)
        self.plus_button.clicked.connect(self.refresh_view)
        self.row_index = 0
        self.project_tree_view.clicked[QtCore.QModelIndex].connect(
            self.row_clicked)
        self.project_tree.dataChanged.connect(self.refresh_view)

    def refresh_view(self):
        self.project_tree_view.expandAll()
        for column in range(self.project_tree_view.model()
                            .columnCount(QtCore.QModelIndex())):
            self.project_tree_view.resizeColumnToContents(column)

    def row_clicked(self, index):
        node = self.project_tree_view.model().data(index, QtCore.Qt.UserRole)
        if self.row_index == index:
            print node.rename
        else:
            self.row_index = index
            #for i in range(self.info_layout.count()):
                #layout = self.info_layout.itemAt(i)
            self.clear_layout(self.info_layout)
            if node.__class__.__name__ == 'Project':
                self.display_project_details(node)
            elif node.__class__.__name__ == 'SimRun':
                self.display_simrun_details(node)
            elif node.__class__.__name__ == 'RessourceNode':
                self.display_source_details(node)

    def display_project_details(self, node):
        form = QtGui.QFormLayout()
        for meta in node.meta:
            label = QtGui.QLabel(meta)
            edit = QtGui.QLineEdit(node.meta[meta])
            edit.setReadOnly(True)
            form.addRow(label, edit)
        self.info_layout.addLayout(form)

    def display_simrun_details(self, node):
        def changeModel(name):
            node.set_model(name)

        form = QtGui.QFormLayout()
        label = QtGui.QLabel('Verkehrsmodell')
        combo = QtGui.QComboBox()
        combo.setEditable(True)
        combo.addItems(node._available)
        combo.currentIndexChanged['QString'].connect(changeModel)
        form.addRow(label, combo)
        self.info_layout.addLayout(form)


    def display_source_details(self, node):
        form = QtGui.QFormLayout()
        label = QtGui.QLabel('Datei')
        edit = QtGui.QLineEdit(node.ressource.source)
        form.addRow(label, edit)
        self.info_layout.addLayout(form)

    def clear_layout(self, layout):
        for i in reversed(range(layout.count())):
            item = layout.itemAt(i)
            if isinstance(item, QtGui.QWidgetItem):
                item.widget().close()
            else:
                self.clear_layout(item.layout())
            layout.removeItem(item)

def startmain():
    app = QtGui.QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    startmain()