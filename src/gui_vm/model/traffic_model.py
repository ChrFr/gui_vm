# -*- coding: utf-8 -*-

##------------------------------------------------------------------------------
## File:        traffic_model.py
## Purpose:     base class for different types of traffic-models to run, load,
##              validate them etc.
##
## Author:      Christoph Franke
##
## Created:
## Copyright:   Gertz Gutsche Rümenapp - Stadtentwicklung und Mobilität GbR
##------------------------------------------------------------------------------

from resources import (H5Array, H5Table, H5Resource, H5TableColumn)
from gui_vm.model.rules import CompareRule, Rule
from resource_dict import (ResourceConfigXMLParser)
from collections import OrderedDict
import numpy as np
import os, imp, sys
from gui_vm.model.observable import Observable
from gui_vm.config.config import Config
from functools import partial
import importlib

config = Config()


class TrafficModel(Observable):
    '''
    base class for traffic models
    '''
    FILENAME_DEFAULT = 'project.xml'

    #names of the fields that can be displayed outside the model
    monitored = OrderedDict()

    def __init__(self, name):
        super(TrafficModel, self).__init__()
        self.name = name

        #dictionary with categories of resources as keys
        #items are lists of the resources to this category
        self.resources = {}

    def process(self):
        pass

    def update(self, path):
        '''
        update all resources in the given project path
        '''
        for resource in self.resources.values():
            resource.update(path)

    def get_resource(self, name):
        '''
        get a resource by name

        Parameters
        ----------
        name: String, name of the resource
        '''
        for res_name in self.resources:
            if res_name == name:
                return self.resources[res_name]
        return None

    def add_resource(self, resource):
        '''
        add a resource to the traffic model

        Parameters
        ----------
        resource: Resource
        '''
        if resource.name in self.resources.keys():
            raise Exception("Resource '{}' defined more than once, "
                            .format(resource.name) +
                            'but the names have to be unique!')
        self.resources[resource.name] = resource

    def add_resources(self, *args):
        '''
        add multiple resource to the traffic model

        Parameters
        ----------
        args: resources
        '''
        for resource in args:
            self.add_resource(resource)

    def validate(self, path):
        '''
        validate all resources in the given project path
        '''
        self.update(path)
        for resource in self.resources:
            resource.validate()

    def resource_config_from_xml(self, filename):
        parser = ResourceConfigXMLParser()
        parser.read(filename)

        # READ AND ADD H5 RESOURCES
        for h5res_node in parser.root.findall('H5Resource'):
            category = h5res_node.attrib['category']
            h5resource = H5Resource(h5res_node.attrib['name'],
                                    subfolder=category,
                                    filename='')
            for sub_node in h5res_node:
                if sub_node.tag == 'H5Table':
                    table = H5Table(sub_node.attrib['path'])
                    table.from_xml(sub_node, reference=self)
                    h5resource.add_child(table)

                elif sub_node.tag == 'H5Array':
                    array = H5Array(sub_node.attrib['path'])
                    array.from_xml(sub_node, reference=self)
                    h5resource.add_child(array)
            self.add_resource(h5resource)


        # MONITOR SPECIFIED RESOURCES
        for monitor in parser.root.findall('Monitor'):
            for monitored in monitor:
                tag = monitored.tag
                # ignore comments and unknown tags
                if tag not in ['content', 'shape']:
                    continue
                monitor_name = monitored.text
                pretty_name = monitored.attrib['alias']
                res_name = monitored.attrib['resource']
                sub_path = monitored.attrib['path']

                self.monitored[monitor_name] = pretty_name
                self.set(monitor_name, None)

                # CONTENT OBSERVATION
                if tag == 'content':
                    col_name = monitored.attrib['column']
                    column = self.resources[res_name].get_child(sub_path).get_child(col_name)
                    # change the value of the monitor (simple attribute with defined name)
                    # each time the column changes
                    column.bind('content', (lambda attr: lambda value: self.set(attr, value))(monitor_name))  # double lambda, because monitor_name changes in closure (-> else always the same name would be taken in callback)

                # SHAPE OBSERVATION (set as properties)
                if tag == 'shape':
                    table = self.resources[res_name].get_child(sub_path)
                    # change the value of the monitor each time shape is reset
                    table.bind('shape', (lambda attr: lambda shape: self.set(attr, int(shape[0]) if shape else None))(monitor_name))

    @property
    def meta(self):
        '''
        create a dictionary out of the monitored attributes

        Return
        ------
        meta: OrderedDict, contains information about the monitored
        attributes
        '''
        meta = OrderedDict()
        for i, attr in enumerate(self.monitored):
            value = getattr(self, attr)
            pretty_name = self.monitored[attr]
            meta[pretty_name] = value
        return meta

    @property
    def options(self):
        return None

    @staticmethod
    def new_specific_model(name):
        traffic_models = config.settings['trafficmodels']
        if name in traffic_models:
            main_path = os.path.split(os.path.split(__file__)[0])[0]
            class_module = traffic_models[name]['class_module']

            module = importlib.import_module(class_module)

            return getattr(module, name)()
        else:
            return None

    # SUBCLASSES HAVE TO OVERRIDE THIS METHOD! (called by the GUI control)
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
        xml_file: absolute path to a xml-file containing the paths to the used resources and the settings for the scenario and run with the given names (gui_vm project-style)
        '''
        pass

    # SUBCLASSES HAVE TO OVERRIDE THIS METHOD! (called by the GUI control)
    def evaluate (self, file_path, overwrite=False):
        '''
        evaluate the demand file at the given path and run the evaluation script
        (creates csv file)

        Parameters
        ----------
        file_path: path to file, the evaluation will be written to
        overwrite: overwrite existing files, if True
        '''
        pass