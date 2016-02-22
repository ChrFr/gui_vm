# -*- coding: utf-8 -*-
from resources import (H5Array, H5Table, H5Resource,
                       CompareRule, H5TableColumn, Rule)
from resource_dict import (TableDict, FileDict, ArrayDict, ColumnDict)
from collections import OrderedDict
import numpy as np
import os, imp, sys
from gui_vm.model.observable import Observable
from gui_vm.config.config import Config
from functools import partial


class TrafficModel(Observable):
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
    FILENAME_DEFAULT = 'project.xml'

    #names of the fields that can be displayed outside the model
    monitored = OrderedDict()

    def __init__(self, name,
                 input_config_file=None, tables_config_file=None,
                 arrays_config_file=None, columns_config_file=None):
        super(TrafficModel, self).__init__()
        self.name = name
        #names of the config files containing the
        #target status of all input data
        self.input_config_file = input_config_file
        self.tables_config_file = tables_config_file
        self.arrays_config_file = arrays_config_file
        self.columns_config_file = columns_config_file
        #create empty tables for the target data and fill them
        self.file_dict = FileDict()
        self.table_dict = TableDict()
        self.array_dict = ArrayDict()
        self.column_dict = ColumnDict()
        if self.input_config_file:
            self.file_dict.from_csv(self.input_config_file)
        if self.tables_config_file:
            self.table_dict.from_csv(self.tables_config_file)
        if self.arrays_config_file:
            self.array_dict.from_csv(self.arrays_config_file)
        if self.columns_config_file:
            self.column_dict.from_csv(self.columns_config_file)

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

    def read_resource_config(self):
        '''
        build the resource tree with according rules out of the csv definitions
        '''
        #variable to store columns that could not be created at the
        #desired point
        delayed_columns = []
        if self.file_dict.row_count > 0:
            unique_resources = np.unique(self.file_dict['resource_name'])
            for res_name in unique_resources:
                res_table = self.file_dict.get_rows_by_entries(
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
                            #get the specific node out of the table dict
                            table_dict = self.table_dict.get_rows_by_entries(
                                resource_name=res_name, subdivision=node_name)
                            node, delayed = table_dict_to_h5table(
                                table_dict, self.column_dict,
                                reference=self)
                            #only one node is expected in return (unique names)
                            node = node[0]
                            delayed_columns.extend(delayed)
                        resource.add_child(node)
                    self.add_resources(resource)

        # compute the delayed columns (joker names)
        for d_col in delayed_columns:
            col_name = d_col['column_name'][0]
            joker = d_col['joker'][0]
            if '?' in col_name or '*' in col_name:

                def add_dynamic_cols(c):
                    field_name = c['joker'][0]
                    replace = self.get(field_name)
                    resource = self.resources[c['resource_name'][0]]
                    h5table = resource.get_child(c['subdivision'][0])
                    tmp = []
                    # remove old dynamic columns
                    # WARNING: removes all dynamic columns, so there can only
                    # be one pattern for dynamic cols per table
                    for i in xrange(len(h5table.children)):
                        col = h5table.children.pop(0)
                        if col.dynamic:
                            col.remove_children()
                        else:
                            tmp.append(col)
                    h5table.children = tmp
                    if not replace:
                        return
                    c_n = c['column_name'][0]
                    c1 = c.clone()
                    c2 = c.clone()
                    c1.clear()
                    # build a column dict with the new column names
                    for r in replace:
                        new_col_name = c_n.replace('?', r).replace('*', r)
                        c2['column_name'] = new_col_name
                        c1.merge_table(c2)
                    #create h5 columns
                    columns = column_dict_to_h5column(c1, reference=self)[0]
                    for col in columns:
                        col.dynamic = True
                        h5table.add_child(col)

                # on change of the field the joker is referenced to,
                # the dynamic cols will be be added
                self.bind(joker, partial((lambda d, value:
                          add_dynamic_cols(d)), d_col))


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
        if self.array_dict.row_count > 0:
            rows = self.array_dict.get_rows_by_entries(
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
                                           reference=reference,
                                           error_msg='Minimum von '
                                           + minimum + ' unterschritten',
                                           success_msg='Minimum überprüft')
                    node.add_rule(min_rule)
                if maximum != '':
                    if is_number(maximum):
                        reference = None
                    else:
                        reference = self
                    max_rule = CompareRule('max_value', '<=', maximum,
                                           reference=reference,
                                           error_msg='Maximum von '
                                           + maximum + ' überschritten',
                                           success_msg='Maximum überprüft')
                    node.add_rule(max_rule)
                if (np.array(dimension) != '').any():
                    if len(dimension) == 1:
                        dimension = dimension[0]
                    dim_rule = CompareRule('shape', '==', dimension,
                                           reference=self,
                                           error_msg='falsche Dimension',
                                           success_msg='Dimension überprüft')
                    node.add_rule(dim_rule)
        return node


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
        config = Config()
        config.read()
        traffic_models = config.settings['trafficmodels']
        if name in traffic_models:
            main_path = os.path.split(os.path.split(__file__)[0])[0]
            config_filename = traffic_models[name]['config_file']
            #complete relative paths
            if not os.path.isabs(config_filename):
                config_filename = os.path.join(main_path,
                                               config_filename)
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

def table_dict_to_h5table(table_dict, column_dict, reference=None):
    '''
    create a resource h5table node

    Parameter
    ---------
    table_dict: TableDict, contains the name of the tables and the resources
                they belong to

    column_dict: ColumnDict, contains the columns that will be added, the
                 tables and resources they belong to and the target
                 values (minimum, maximum, type, is_primary_key)

    reference:  object, optional
                a referenced object, created rules are (e.g. min with fieldname)
                referenced to this object

    Return
    ------
    tables: list of H5Tables, the created tables with all target values, rules
            and columns(as defined in the table config)

    ignored: list of ColumnDicts, columns that could not be created yet
    '''
    tables = []
    ignored = []
    node_names = table_dict['subdivision']
    resource_names = table_dict['resource_name']
    for row in xrange(table_dict.row_count):
        node_name = node_names[row]
        res_name = resource_names[row]
        h5table = H5Table(node_name)
        table = table_dict.get_rows_by_entries(
            resource_name=res_name, subdivision=node_name)
        if table.row_count > 0:
            if table.row_count > 1:
                raise Exception('{}{} defined more than once'
                                .format(res_name, node_name))
            n_rows = table['n_rows'][0]
            if n_rows != '':
                dim_rule = CompareRule('shape', '==',
                                       n_rows, reference=reference,
                                       error_msg='falsche Dimension',
                                       success_msg='Dimension überprüft')
                h5table.add_rule(dim_rule)

            #add columns required by the model to table (defined in csv)
            table_cols = column_dict.get_rows_by_entries(
                resource_name=res_name, subdivision=node_name)
            columns, ign = column_dict_to_h5column(table_cols,
                                                   reference=reference)
            ignored.extend(ign)
            for column in columns:
                h5table.add_child(column)
            tables.append(h5table)
    return tables, ignored


def column_dict_to_h5column(column_dict, reference=None, ignore_jokers=True):
    '''
    create a resource table node

    Parameter
    ---------
    column_dict: ColumnDict, containing the name of the columns and the target
                 values (minimum, maximum, type, is_primary_key)

    reference:  object, optional
                a referenced object, created rules are (e.g. min with fieldname)
                referenced to this object

    ignore_jokers:  bool, optional
                    ignore columns with joker chars (their names
                    depend on other columns)?

    Return
    ------
    columns: list of H5TableColumns, the created columns with target values as rules
            (as defined in the table_dict)
    ignored: list of ColumnDicts, columns that could not be created yet
    '''
    ignored = []
    columns = []
    for row in xrange(column_dict.row_count):
        col_name = column_dict['column_name'][row]
        column = column_dict.get_rows_by_entries(
            column_name = col_name)
        dtype = column['type'][0]
        minimum = column['minimum'][0]
        maximum = column['maximum'][0]
        primary = column['is_primary_key'][0]
        #ignore columns depending on other columns (identified by joker chars)
        if ignore_jokers and ('?' in col_name or '*' in col_name):
            ignored.append(column)
            continue
        if primary == '1' or primary == 'True':
            is_primary_key = True
        else:
            is_primary_key = False
        column = H5TableColumn(col_name,
                               exp_dtype=dtype,
                               exp_minimum=minimum,
                               exp_maximum=maximum,
                               is_primary_key=is_primary_key,
                               reference=reference,
                               required=True)
        columns.append(column)
    return columns, ignored
