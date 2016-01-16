# -*- coding: utf-8 -*-
from argparse import ArgumentParser
import sys
import os

from gui_vm.model.project_tree import XMLParser, TreeNode
from gui_vm.get_param_from_config import Params

def main():
    parser = ArgumentParser(description="GUI Verkehrsmodelle - List Scenarios")

    parser.add_argument("-o", action="store",
                        help="vorhandene XML-Projektdatei öffnen",
                        dest="project_file", default=None)


    options = parser.parse_args()

    # read Scenario from xml-Project-File
    p = Params(options.project_file)
    scenarios = p.get_scenarios()

    for scenario in scenarios:
        print(scenario)


if __name__ == "__main__":
    main()
