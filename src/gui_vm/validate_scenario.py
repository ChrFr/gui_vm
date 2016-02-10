# -*- coding: utf-8 -*-
from argparse import ArgumentParser
import sys
from gui_vm.control.main_control import MainWindow
from gui_vm.model.project_tree import Scenario, OutputNode
from PyQt4 import QtGui

def startmain():
    parser = ArgumentParser(description="GUI Verkehrsmodelle - validate Scenario")

    parser.add_argument("-f", '--xml', action="store",
                        help="vorhandene XML-Projektdatei öffnen",
                        dest="project_file", default=None)

    parser.add_argument("-s", '--scenario', action="store",
                        help="angegebenes Szenario prüfen",
                        dest="scenario_name", default=None)

    arguments = parser.parse_args()

    app = QtGui.QApplication(sys.argv)
    project_file = arguments.project_file
    scenario_name = arguments.scenario_name
    ret = ''

    mainwindow = MainWindow.only_validate(project_file, scenario_name)
    mainwindow.show()
    ret = app.exec_()
    if ret < 0:
        raise RuntimeError('The GUI caused a problem')
    ret = ''
    selected_item = mainwindow.project_control.selected_item
    try:
        while not isinstance(selected_item, (Scenario, OutputNode)):
            selected_item = selected_item.parent
        else:
            if isinstance(selected_item, OutputNode):
                selected_run = selected_item.name
                ret = 'selected run:{run}\n'.format(run=selected_run)
                while not isinstance(selected_item, Scenario):
                    selected_item = selected_item.parent
            scenario_name = selected_item.name
            ret += 'selected scenario:{sc}'.format(sc=scenario_name)
            mainwindow.validated = True
    except AttributeError:
        ret = 'no scenario selected'
        # ggf. Abbruch-Button hinzufügen...
    sys.exit(ret)


if __name__ == "__main__":
    startmain()