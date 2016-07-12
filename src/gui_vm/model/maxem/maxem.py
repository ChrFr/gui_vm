# -*- coding: utf-8 -*-
from gui_vm.model.traffic_model import TrafficModel
from gui_vm.model.rules import Rule
from collections import OrderedDict
import subprocess
import os, imp
import sys
import csv
import numpy as np
from gui_vm.config.config import Config, Singleton
import gui_vm

config = Config()

class Maxem(TrafficModel):
    '''
    Maxem traffic model
    '''
    #__metaclass__ = Singleton
    # singleton won't work because of resource paths, TODO: clone in TrafficModel to avoid multiple readings

    # name of the config file containing the target status of all input data
    # relative to the directory this file is in
    RESOURCES_XML = 'Maxem.xml'
    EVALUATION_SCRIPT = 'evaluate_maxem.py'

    def __init__(self):
        super(Maxem, self).__init__('Maxem')
        maxem_path = os.path.dirname(__file__)
        resource_xml_file = os.path.join(maxem_path, self.RESOURCES_XML)
        self.resource_config_from_xml(resource_xml_file)

    def evaluate (self, file_path, overwrite=False):
        '''
        evaluate the demand file at the given path and run the evaluation script
        (creates csv file)
        '''
        eval_script = os.path.join(os.path.dirname(__file__), self.EVALUATION_SCRIPT)
        Evaluation = (imp.load_source('evaluate', eval_script))
        if file_path is None:
            return None
        csv_out = file_path.replace('.h5', '.csv')
        if not os.path.exists(file_path):
            return None
        if overwrite or not os.path.exists(csv_out):
            Evaluation.evaluate(file_path, csv_out)
        with open(csv_out, mode='r') as csv_in:
            reader = csv.reader(csv_in)
            table_dict = OrderedDict()
            for i, rows in enumerate(reader):
                for k, h in enumerate(rows):
                    #header
                    if i == 0:
                        table_dict[h] = []
                    #column
                    else:
                        table_dict[table_dict.keys()[k]].append(h)

        return table_dict

    def run(self, scenario_name, process, callback=None,
            on_success=None, xml_file=None, run_name=None):
        '''
        run the traffic model

        Parameters
        ----------
        scenario_name: String, name of the scenario
        process: a clean qtProcess to run the model in
        callback: function to track the progress
        on_success: is executed after successfully running the model
        run_name: name of the run inside the scenario
        xml_file: absolute path th a xml-file containing the paths to the used resources and the settings for the scenario and run with the given names (gui_vm project-style)
        '''
        python_path = config.settings['trafficmodels'][self.name]['interpreter']
        executable = config.settings['trafficmodels'][self.name]['executable']
        #executable = '-m tdmks.main'
        cmd = python_path + ' ' + executable
        cmd_scen_name = '-n "{}"'.format(scenario_name)

        if run_name is not None:
            cmd_run_name = '-r "{}"'.format(run_name)
        else:
            cmd_run_name=''

        if xml_file is not None:
            cmd_xml_file = '-xml "{}"'.format(xml_file)
        else:
            cmd_xml_file=''

        full_cmd = ' '.join([cmd, cmd_scen_name, cmd_run_name, cmd_xml_file])

        self.already_done = 0.
        self.group = None
        groups_count = len(self.get('groups_dest_mode'))
        self.to_do = 0
        self.group_share = 100. / groups_count
        self.group_counter = 0

        def progress():
            message = str(process.readAllStandardError())
            l = message.split("INFO->['")
            if len(l)>1:
                l2 = l[1].split("'")
                new_group = l2[0]
                l3 = l[1].split(',')
                self.to_do = max(self.to_do, int(l3[1].strip()))
                self.already_done += self.group_share / self.to_do
                if self.group != new_group:
                    self.group = new_group
                    self.group_counter += self.group_share
                    self.to_do = 0
            if callback:
                callback(message, self.already_done)
            # ' ... completed' is final success message of tdmks run
            if 'completed' in message:
                if on_success:
                    on_success()
        #ToDo: how to check if error occured (tdmks doesn't return exit codes)

        # QProcess emits `readyRead` when there is data to be read
        process.readyReadStandardOutput.connect(progress)
        process.readyReadStandardError.connect(progress)
        #process.finished.connect(self.finished)

        # log the command issued
        if callback:
            callback(full_cmd, 0)
        # start
        process.start(full_cmd)