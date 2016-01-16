# -*- coding: utf-8 -*-
from argparse import ArgumentParser
import sys
from gui_vm.control.main_control import MainWindow
from PyQt4 import QtGui

def clone():
    parser = ArgumentParser(description="GUI Verkehrsmodelle")

    parser.add_argument("-o", action="store",
                        help="vorhandene XML-Projektdatei öffnen",
                        dest="project_file")

    parser.add_argument("-t", '--template', action="store",
                        help="angegebenes Szenario klonen",
                        dest="template_name")

    parser.add_argument("-s", '--scenario', action="store",
                        help="neuer Szenario-Name",
                        dest="scenario_name")

    arguments = parser.parse_args()

    app = QtGui.QApplication(sys.argv)
    project_file = arguments.project_file
    template = arguments.template
    new_scenario = arguments.scenario_name

    # hier die Clone-Methode aufrufen!

    #mainwindow = MainWindow(project_file = project_file,
                            #run_scenario = run_scenario)
    #mainwindow.show()
    #sys.exit(app.exec_())

if __name__ == "__main__":
    clone()