# -*- coding: utf-8 -*-
from gui_vm.model.traffic_model import TrafficModel
from gui_vm.model.resources import Rule
from collections import OrderedDict
import subprocess
import os
import sys
from gui_vm.config.config import Config

config = Config()
config.read()

class SpecificModel(TrafficModel):
    '''
    Maxem traffic model
    '''

    #names of the config files containing the target status of all input data
    #relative to the directory this file is in
    INPUT_CONFIG_FILE = 'Maxem_input.csv'
    TABLES_CONFIG_FILE = 'Maxem_tables.csv'
    ARRAYS_CONFIG_FILE = 'Maxem_arrays.csv'
    COLUMNS_CONFIG_FILE = 'Maxem_columns.csv'

    #names of the fields that can be displayed outside the model
    #can be adressed in the csv as fields of the table
    monitored = OrderedDict([('n_zones', 'Anzahl Zonen'),
                             ('n_time_series', 'Anzahl Zeitscheiben'),
                             ('n_activity_pairs', 'Aktivitaetenpaare'),
                             ('activity_names', 'Aktivitaeten'),
                             ('activity_codes', 'Aktivitaetencodes')])

    def __init__(self, path=None):
        input_config_file = os.path.join(os.path.dirname(__file__),
                                         self.INPUT_CONFIG_FILE)
        tables_config_file = os.path.join(os.path.dirname(__file__),
                                         self.TABLES_CONFIG_FILE)
        arrays_config_file = os.path.join(os.path.dirname(__file__),
                                         self.ARRAYS_CONFIG_FILE)
        columns_config_file = os.path.join(os.path.dirname(__file__),
                                         self.COLUMNS_CONFIG_FILE)
        super(SpecificModel, self).__init__(
            'Maxem',
            input_config_file=input_config_file,
            tables_config_file=tables_config_file,
            arrays_config_file=arrays_config_file,
            columns_config_file=columns_config_file)


        ####special rules for the maxem model#####

        if path is not None:
            self.update()

    @property
    def n_zones(self):
        #number of zones is determined by the number of rows in
        #/zones/zones
        shape = self.resources['Zonen'].get_child('/zones/zones').shape
        if shape is None:
            return None
        else:
            return int(shape[0])

    @property
    def n_time_series(self):
        #time series is determined by the number of rows in
        #/activities/time_series
        shape = self.resources['Params'].get_child('/activities/time_series').shape
        if shape is None:
            return None
        else:
            return int(shape[0])

    @property
    def n_activity_pairs(self):
        shape = self.resources['Params'].get_child('/activities/activitypairs').shape
        if shape is None:
            return None
        else:
            return int(shape[0])

    @property
    def activity_codes(self):
        return self.resources['Params'].get_content('/activities/activities', 'code')

    @property
    def activity_names(self):
        return self.resources['Params'].get_content('/activities/activities', 'name')

    def update(self, path):
        super(SpecificModel, self).update(path)

    def run(self, scenario_name, process, resources,
            callback=None, modal_split=False, correction=False):
        '''
        run the traffic model

        Parameters
        ----------
        scenario_name: String, name of the scenario
        resources: list of ResourceNodes, contains the resources that will be
                   given to the executable as parameters
        modal_split, correction: bool, optional
                                 do preprocessing (or don't)
        callback: function,
                  function to track the progress
        '''
        #dictionary to map the resource names to parameters of the executable
        params = {
            'Zonen': '--zd',
            'OV': '--pp_put --put',
            'MIV': '--pp_prt --prt',
            'Fuss und Rad': '--pp_nmt --nmt',
            'Betas': '--par',
        }

        python_path = config.settings['environment']['python_path']
        executable = config.settings['trafficmodels'][self.name]['executable']
        #cmd = r'C:\Anaconda\envs\tdmks\python -m tdmks.main'
        cmd = python_path + ' ' + executable
        cmd_name = '-n "{}"'.format(scenario_name)

        param_cmd = ''
        for res in resources:
            src = res.full_source
            if len(src) > 0 and res.name in params:
                param_cmd += ' {0} "{1}"'.format(params[res.name],
                                                 res.full_source)

        if modal_split:
            cmd_cal = '-c'
        else:
            cmd_cal=''

        if correction:
            cmd_kor = '--update_kf'
        else:
            cmd_kor=''

        # create full command
        full_cmd = ' '.join([cmd, cmd_name, param_cmd, cmd_cal, cmd_kor])

        self.group = None
        self.progressMax = 15
        def show_progress():
            if callback:
                message = str(process.readAllStandardError())
                already_done = None
                l = message.split("INFO->['")
                if len(l)>1:
                    l2 = l[1].split("'")
                    new_group = l2[0]
                    l3 = l[1].split(',')
                    to_do = int(l3[1].strip())
                    if self.group != new_group:
                        self.group = new_group
                        self.progressMax = to_do
                    already_done = self.progressMax - to_do
                callback(message, already_done)

        # QProcess emits `readyRead` when there is data to be read
        process.readyReadStandardOutput.connect(show_progress)
        process.readyReadStandardError.connect(show_progress)

        process.start(full_cmd)


class ActivityTracking(Rule):
    '''
    special rule to determine if the activity codes are represented in
    a table

    Parameter
    --------
    field_name: String, name of the field that contains the column names
    identifier: String, common name of the columns, the ? will be replaced
                with the activity code
    referenced_field: String, name of the field of the referenced object that
                      holds the activities
    reference: object, the object that holds the activities
    '''

    def __init__(self, field_name, identifier, referenced_field, reference):
        self.identifier = identifier
        super(ActivityTracking, self).__init__(field_name, referenced_field,
                                               self.is_in, reference=reference)

    def is_in(self, column_names, activity_list):
        '''
        check if activity is represented in the columns
        '''
        if activity_list is None:
            return False, 'Aktivität nicht definiert'
        #make activity list iterable (e.g. if only one activity)
        if not hasattr(activity_list, '__iter__'):
            activity_list = [activity_list]

        for activity in activity_list:
            col_name = self.identifier
            col_name = col_name.replace('?', activity)
            if col_name not in column_names:
                return False, 'Spalte {} fehlt'.format(col_name)
        return True, 'Aktivitäten vorhanden'