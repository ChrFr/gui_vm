# -*- coding: utf-8 -*-
from argparse import ArgumentParser
import sys
from gui_vm.control.main_control import MainWindow
from PyQt4 import QtGui

def startmain():
    parser = ArgumentParser(description="GUI Verkehrsmodelle")

    parser.add_argument("--admin", action="store_true",
                        help="Administrationsmodus mit erweiterten Rechten",
                        dest="admin", default=False)

    parser.add_argument("-o", action="store",
                        help="vorhandene XML-Projektdatei öffnen",
                        dest="project_file", default=None)

    parser.add_argument("--scenario", "-s", action="store",
                        help="angegebenes Szenario ausführen",
                        dest="scenario_name", default=None)

    parser.add_argument("--run-specific", "-r", action="store",
                        help="Lauf ausführen",
                        dest="run_name", default="Gesamtlauf")
    parser.add_argument("--calibrate", "-c", action="store_true",
                        help="Kalibrierung durchführen (gilt nur für Gesamtlauf)",
                        dest="calibrate", default=False)

    parser.add_argument("--no-balancing", action="store_false",
                        help="Randsummenabgleich deaktivieren (gilt nur für Gesamtlauf)",
                        dest="do_balancing", default=True)


    arguments = parser.parse_args()

    app = QtGui.QApplication(sys.argv)
    admin_mode = arguments.admin
    project_file = arguments.project_file
    run_scenario = arguments.scenario_name
    run_name = arguments.run_name
    calibrate = arguments.calibrate
    do_balancing = arguments.do_balancing
    ret = -1

    if run_scenario and not project_file:
        print('Um ein Szenario ausführen zu können, muss eine Projektdatei angegeben werden')
        ret = -1
    else:
        mainwindow = MainWindow(project_file=project_file,
                                run_scenario=run_scenario,
                                admin_mode=admin_mode)
        mainwindow.show()
        if run_scenario:
            # main window closes after closing run dialog, because not exec_()
            mainwindow.batch_run(scenario_name=run_scenario, run_name=run_name, do_calibrate=calibrate, do_balancing=do_balancing)
        else:
            ret = app.exec_()
    sys.exit(ret)

if __name__ == "__main__":
    startmain()