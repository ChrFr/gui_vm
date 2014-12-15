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
    INPUT_CONFIG_FILE = ''
    TABLES_CONFIG_FILE = ''
    ARRAYS_CONFIG_FILE = ''
    COLUMNS_CONFIG_FILE = ''

    #names of the fields that can be displayed outside the model
    monitored = OrderedDict()

    def __init__(self, path=None):
        input_config_file = os.path.join(os.path.dirname(__file__),
                                         self.INPUT_CONFIG_FILE)
        tables_config_file = os.path.join(os.path.dirname(__file__),
                                         self.TABLES_CONFIG_FILE)
        arrays_config_file = os.path.join(os.path.dirname(__file__),
                                         self.ARRAYS_CONFIG_FILE)
        columns_config_file = os.path.join(os.path.dirname(__file__),
                                         self.COLUMNS_CONFIG_FILE)
        super(Verkmod, self).__init__(
            'VerkMod',
            input_config_file=input_config_file,
            tables_config_file=tables_config_file,
            arrays_config_file=arrays_config_file,
            columns_config_file=columns_config_file)


    def update(self, path):
        super(Verkmod, self).update(path)

    def process():
        pass

