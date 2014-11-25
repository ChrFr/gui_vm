from resources import (H5Array, H5Table, H5Resource,
                       CompareRule, H5TableColumn, Rule)
from resource_parser import (TableTable, InputTable, ArrayTable, ColumnTable)
from collections import OrderedDict
import numpy as np
import os, imp
from gui_vm.config.config import Config


class TrafficModel(object):
    '''
    base class for traffic models

    Parameter
    ---------
    input_config_file: String, optional
                       name of the csv file that holds information about all
                       input files, tables etc.
    tables_config_file: String, optional
                        name of the csv file that holds information about all
                        tables and their target values
    arrays_config_file: String, optional
                        name of the csv file that holds information about all
                        tables and their target values
    columns_config_file: String, optional
                         name of the csv file that holds information about all
                         tablecolumns and their target values

    '''
    FILENAME_DEFAULT = 'default.xml'

    #names of the fields that can be displayed outside the model
    monitored = OrderedDict()

    def __init__(self, name,
                 input_config_file=None, tables_config_file=None,
                 arrays_config_file=None, columns_config_file=None):
        self.name = name
        #names of the config files containing the
        #target status of all input data
        self.input_config_file = input_config_file
        self.tables_config_file = tables_config_file
        self.arrays_config_file = arrays_config_file
        self.columns_config_file = columns_config_file
        #create empty tables for the target data and fill them
        self.input_table = InputTable()
        self.tables_table = TableTable()
        self.array_table = ArrayTable()
        self.column_table = ColumnTable()
        if self.input_config_file:
            self.input_table.from_csv(self.input_config_file)
        if self.tables_config_file:
            self.tables_table.from_csv(self.tables_config_file)
        if self.arrays_config_file:
            self.array_table.from_csv(self.arrays_config_file)
        if self.columns_config_file:
            self.column_table.from_csv(self.columns_config_file)

        #dictionary with categories of resources as keys
        #items are lists of the resources to this category
        self.resources = {}
        self.read_config()

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

    def add_resources(self, *args):
        '''
        add a resource to the traffic model

        Parameters
        ----------
        resource: Resource
        '''
        for resource in args:
            if resource.name in self.resources.keys():
                raise Exception("Resource '{}' defined more than once, "
                                .format(resource.name) +
                                'but the names have to be unique!')
            self.resources[resource.name] = resource

    def validate(self, path):
        '''
        validate all resources in the given project path
        '''
        self.update(path)
        for resource in self.resources:
            resource.validate()

    def read_config(self):
        '''
        build the resource tree with according rules out of the csv definitions
        '''
        if self.input_table.row_count > 0:
            unique_resources = np.unique(self.input_table['resource_name'])
            for res_name in unique_resources:
                res_table = self.input_table.get_rows_by_entries(
                    resource_name=res_name)
                category = str(res_table['category'][0])
                if res_table['type'][0].startswith('H5'):
                    resource = H5Resource(str(res_name),
                                          subfolder=category,
                                          filename='')
                    node_names = res_table['subdivision']
                    node_types = res_table['type']
                    for i, node_name in enumerate(node_names):
                        node_type = node_types[i]
                        #read and add rules for arrays
                        if node_type == 'H5Array':
                            node = self.create_H5ArrayNode(res_name,
                                                           node_name)
                        #read and add rules for arrays
                        elif node_type == 'H5Table':
                            node = self.create_H5TableNode(res_name,
                                                           node_name)
                        resource.add_child(node)
                    self.add_resources(resource)

    def create_H5ArrayNode(self, res_name, node_name):
        '''
        create a resource array node

        Parameter
        ---------
        res_name: String, name of the resource the node belongs to
        node_name: String, the name the node will get

        Return
        ------
        node: H5Array, the new node with all target values and rules
              (as defined in the array config)
        '''
        node = H5Array(node_name)
        if self.array_table.row_count > 0:
            rows = self.array_table.get_rows_by_entries(
                resource_name=res_name, subdivision=node_name)
            if rows.row_count > 1:
                raise Exception('{}{} defined more than once in {}'.format(
                    res_name, node_name, self.arrays_config_file))
            if rows.row_count > 0:
                minimum = rows['minimum'][0]
                maximum = rows['maximum'][0]
                dimension = tuple(rows['dimension'][0].split(' x '))
                if minimum != '':
                    if is_number(minimum):
                        reference = None
                    else:
                        reference = self
                    min_rule = CompareRule('min_value', '>=', minimum,
                                           reference=reference)
                    node.add_rule(min_rule)
                if maximum != '':
                    if is_number(maximum):
                        reference = None
                    else:
                        reference = self
                    max_rule = CompareRule('max_value', '<=', maximum,
                                           reference=reference)
                    node.add_rule(max_rule)
                if (np.array(dimension) != '').any():
                    if len(dimension) == 1:
                        dimension = dimension[0]
                    dim_rule = CompareRule('shape', '==', dimension,
                                           reference=self)
                    node.add_rule(dim_rule)
        return node

    def create_H5TableNode(self, res_name, node_name):
        '''
        create a resource table node

        Parameter
        ---------
        res_name: String, name of the resource the node belongs to
        node_name: String, the name the node will get

        Return
        ------
        node: H5Array, the new node with all target values, rules and columns
              (as defined in the array config)
        '''
        node = H5Table(node_name)
        if self.tables_table.row_count > 0:
            rows = self.tables_table.get_rows_by_entries(
                resource_name=res_name, subdivision=node_name)
            if rows.row_count > 0:
                if rows.row_count > 1:
                    raise Exception('{}{} defined more than once in {}'
                                    .format(res_name, node_name,
                                            self.tables_config_file))
                n_rows = rows['n_rows'][0]
                if n_rows != '':
                    dim_rule = CompareRule('shape', '==',
                                           n_rows, reference=self)
                    node.add_rule(dim_rule)
                #add check of dtypes
                table_cols = self.column_table.get_rows_by_entries(
                    resource_name=res_name, subdivision=node_name)
                col_names = table_cols['column_name']
                dtypes = table_cols['type']
                minima = table_cols['minimum']
                maxima = table_cols['maximum']
                primaries = table_cols['is_primary_key']
                #add the columns with their rules
                for row in xrange(table_cols.row_count):
                    col_name = col_names[row]
                    dtype = dtypes[row]
                    minimum = minima[row]
                    maximum = maxima[row]
                    primary = primaries[row]
                    if primary == '1' or primary == 'True':
                        is_primary = True
                    else:
                        is_primary = False
                    col = H5TableColumn(col_name, is_primary)
                    if minimum != '':
                        if is_number(minimum):
                            reference = None
                        else:
                            reference = self
                        min_rule = CompareRule('min_value', '>=', minimum,
                                               reference=reference)
                        col.add_rule(min_rule)
                    if maximum != '':
                        if is_number(maximum):
                            reference = None
                        else:
                            reference = self
                        max_rule = CompareRule('max_value', '<=', maximum,
                                               reference=reference)
                        col.add_rule(max_rule)
                    if dtype != '':
                        type_rule = CompareRule('dtype', '==', dtype)
                        col.add_rule(type_rule)
                    node.add_child(col)
        return node

    @property
    def characteristics(self):
        '''
        create a dictionary out of the monitored attributes

        Return
        ------
        characteristics: OrderedDict, contains information about the monitored
                         attributes
        '''
        characteristics = OrderedDict()
        for i, attr in enumerate(self.monitored):
            value = getattr(self, attr)
            pretty_name = self.monitored[attr]
            characteristics[pretty_name] = value
        return characteristics

    @staticmethod
    def new_specific_model(name):
        config = Config()
        config.read()
        traffic_models = config.settings['trafficmodels']
        if name in traffic_models:
            config_filename = traffic_models[name]['config_file']
            #complete relative paths
            if not os.path.isabs(config_filename):
                config_filename = os.path.join(os.getcwd(), config_filename)
            return (imp.load_source('SpecificModel', config_filename)
                    .SpecificModel())
        else:
            return None

def is_number(s):
    '''
    check if String represents a number
    '''
    try:
        float(s)
        return True
    except ValueError:
        return False
