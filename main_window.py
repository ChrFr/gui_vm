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
        self.project_tree_view.clicked[QtCore.QModelIndex].connect(self.row_clicked)
        self.project_tree.dataChanged.connect(self.refresh_view)

    def refresh_view(self):
        self.project_tree_view.expandAll()
        for column in range(self.project_tree_view.model()
                            .columnCount(QtCore.QModelIndex())):
            self.project_tree_view.resizeColumnToContents(column)

    def row_clicked(self, index):
        if self.row_index == index:
            node = self.project_tree_view.model().data(index, QtCore.Qt.UserRole)
            print node.rename
        else:
            self.row_index = index
            #details = self.project_tree_view.get_details(index)
            #self.display_details(details)

    def display_details(self, details):
        pass

def startmain():
    app = QtGui.QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    startmain()