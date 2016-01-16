# -*- coding: utf-8 -*-
from argparse import ArgumentParser
import sys
import os

from gui_vm.model.project_tree import XMLParser, TreeNode


class Params(object):
    """get params from an xml file

    Parameters
    ----------

    project_file : str
        the path to the project-xml-file to open
    """

    def __init__(self,
                 project_file):
        self.root = TreeNode('root')
        XMLParser.read_xml(self.root, project_file)
        self.project_folder = os.path.split(project_file)[0]

    def get_params_of_scenario(self, scenario_name, params):
        """
        params : list of str
            a list of names of the parameters to parse

        scenario_name : str
            the name of the scenario
        """
        scenario = self.root.find_all(scenario_name)[0]
        param_values = []
        for param_name in params:
            scenario_param = scenario.find_all(param_name.strip("\""))
            if not scenario_param:
                raise ValueError('scenario {} not found'.format(scenario_name))

            param_values.append(scenario_param[-1])
        return param_values


def main():
    parser = ArgumentParser(description="GUI Verkehrsmodelle")

    parser.add_argument("-o", action="store",
                        help="vorhandene XML-Projektdatei öffnen",
                        dest="project_file", default=None)

    parser.add_argument("-s", '--scenario', action="store",
                        help="angegebenes Szenario ausführen",
                        dest="scenario_name", default=None)

    parser.add_argument("-p", '--params', action="store",
                       help="Parameter ausgeben", nargs='+',
                       dest="param_names", default=None)

    options = parser.parse_args()

    # read Scenario from xml-Project-File
    p = Params(options.project_file)
    param_values = p.get_params_of_scenario(options.scenario_name,
                                            options.param_names)

    for param_value in param_values:
        path = os.path.join(p.project_folder,
                            options.scenario_name,
                            param_value.file_relative)
        print(path)


if __name__ == "__main__":
    main()
