# -*- coding: utf-8 -*-
from gui_vm.model.traffic_model import TrafficModel
from gui_vm.model.resources import Rule
from collections import OrderedDict
import subprocess
import os
import sys
import numpy as np
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
                             ('area_types', 'Gebietstypen'),
                             ('n_time_series', 'Anzahl Zeitscheiben'),
                             ('n_activity_pairs', 'Aktivitätenpaare'),
                             ('activity_names', 'Aktivitäten'),
                             ('activity_codes', 'Aktivitätencodes'),
                             ('group_dest_mode', 'Personengruppen')])

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

        self.activity_codes = None
        self.activity_names = None
        self.group_dest_mode = None
        self.area_types = None

        self.read_resource_config()

        ####observe columns####
        activities = self.resources['Params'].get_child(
            '/activities/activities')
        #observe activity codes
        code_column = activities.get_child('code')
        code_column.bind('content',
                         lambda value: self.set('activity_codes', value))
        #observe activity names
        name_column = activities.get_child('name')
        name_column.bind('content',
                         lambda value: self.set('activity_names', value))
        #observe area_types
        zones = self.resources['Zonen'].get_child('/zones/zones')
        area_column = zones.get_child('area_type')
        def area_unique(value):
            if value:
                self.set('area_types', np.unique(value))
        area_column.bind('content',
                         lambda value: area_unique(value))

        groups = self.resources['Params'].get_child(
            '/groups/groups_dest_mode')
        #observe group destination modes
        grp_column = groups.get_child('code')
        grp_column.bind('content',
                         lambda value: self.set('group_dest_mode',
                                                value))

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

    def update(self, path):
        super(SpecificModel, self).update(path)

    def evaluate (self, output_node):
        a = output_node.get('/modes/bicycle')
        meta = OrderedDict()
        #meta['Gesamtsumme der Wege'] = 'Hallo'
        return meta

    def run(self, scenario_name, process, resources, output_path=None,
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
        cmd = python_path + ' ' + executable
        cmd_name = '-n "{}"'.format(scenario_name)

        param_cmd = ''
        for res in resources:
            src = res.file_absolute
            if len(src) > 0 and res.name in params:
                param_cmd += ' {0} "{1}"'.format(params[res.name],
                                                 res.file_absolute)

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
        if output_path:
            cmd_demand = '-dp "{}"'.format(output_path)
            full_cmd = ' '.join([full_cmd, cmd_demand])

        self.already_done = 0.
        self.group = None
        groups_count = len(self.get('group_dest_mode'))
        self.to_do = 0
        self.group_share = 100. / groups_count
        self.group_counter = 0

        def show_progress():
            if callback:
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
                callback(message, self.already_done)

        # QProcess emits `readyRead` when there is data to be read
        process.readyReadStandardOutput.connect(show_progress)
        process.readyReadStandardError.connect(show_progress)
        #process.finished.connect(self.finished)
        process.start(full_cmd)