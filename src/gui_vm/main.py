# -*- coding: utf-8 -*-
from argparse import ArgumentParser
import sys
from gui_vm.control.main_control import MainWindow
from PyQt4 import QtGui

def startmain():
    parser = ArgumentParser(description="GUI Verkehrsmodelle")

    parser.add_argument("-o", action="store",
                        help="vorhandene XML-Projektdatei öffnen",
                        dest="project_file", default=None)

    parser.add_argument("-run", action="store",
                        help="angegebenes Szenario ausführen",
                        dest="scenario_name", default=None)

    arguments = parser.parse_args()

    app = QtGui.QApplication(sys.argv)
    project_file = arguments.project_file
    run_scenario = arguments.scenario_name
    if run_scenario and not project_file:
        print('Um ein Szenario ausführen zu können, muss eine Projektdatei angegeben werden')
    else:
        mainwindow = MainWindow(project_file = project_file,
                                run_scenario = run_scenario)
        mainwindow.show()
        sys.exit(app.exec_())

def clone_scenario():
    parser = ArgumentParser(description="GUI Verkehrsmodelle")

    parser.add_argument("-o", action="store",
                        help="vorhandene XML-Projektdatei öffnen",
                        dest="project_file")

    parser.add_argument("-t", action="store",
                        help="Name des zu klonenden Szenarios",
                        dest="template")

    parser.add_argument("-s", action="store",
                        help="Name des zu erstellenden, geklonten Szenarios",
                        dest="new_scenario")

    arguments = parser.parse_args()

    app = QtGui.QApplication(sys.argv)
    project_file = arguments.project_file
    template = arguments.template
    new_scenario_name = arguments.new_scenario
    mainwindow = MainWindow(project_file = project_file)
    mainwindow.show()
    mainwindow.clone_scenario(template, new_scenario_name)

if __name__ == "__main__":
    startmain()