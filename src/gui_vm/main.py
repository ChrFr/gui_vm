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
        ret = -1
    else:
        mainwindow = MainWindow(project_file=project_file,
                                run_scenario=run_scenario)
        if run_scenario:
            mainwindow.project_control.run(scenario_name=run_scenario)
        mainwindow.show()
        ret = app.exec_()
    sys.exit(ret)

if __name__ == "__main__":
    startmain()