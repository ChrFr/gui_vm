# -*- coding: utf-8 -*-
import sys
from gui_vm.control.main_control import MainWindow
from PyQt4 import QtGui

def startmain():
    app = QtGui.QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    startmain()