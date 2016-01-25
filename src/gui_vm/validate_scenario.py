# -*- coding: utf-8 -*-
from argparse import ArgumentParser
import sys
from gui_vm.control.main_control import MainWindow
from gui_vm.model.project_tree import Scenario
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

    mainwindow = MainWindow.only_validate(project_file, scenario_name)
    while not mainwindow.validated:
        mainwindow.show()
        ret = app.exec_()
        selected_item = mainwindow.project_control.selected_item
        try:
            while not isinstance(selected_item, Scenario):
                selected_item = selected_item.parent
            else:
                scenario_name = selected_item.name
                if selected_item.is_valid:
                    ret ='selected scenario:{sc}'.format(sc=scenario_name)
                else:
                    ret = 'scenario {sc} invalid'.format(sc=scenario_name)
                mainwindow.validated = True
        except AttributeError:
            ret = 'no scenario selected'
            # ggf. Abbruch-Button hinzufügen...
    else:
        ret = 'selected scenario:{sc}'.format(sc=scenario_name)
    sys.exit(ret)


if __name__ == "__main__":
    startmain()