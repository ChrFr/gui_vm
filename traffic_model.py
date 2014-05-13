from resources import (H5Array, H5Table, H5Resource, Rule)
from backend import (TableTable, InputTable, ArrayTable, ColumnTable)
import numpy as np

class TrafficModel(object):
    '''
    base class for traffic models
    '''

    def __init__(self, name):
        self.name = name
        self.input_config_file = None
        self.tables_config_file = None
        self.arrays_config_file = None
        self.columns_config_file = None
        #dictionary with categories of resources as keys
        #items are lists of the resources to this category
        self.resources = {}

    def process(self):
        pass

    def update(self, path):
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
            self.resources[resource.name] = resource

    def validate(self, path):
        self.update(path)
        for resource in self.resources:
            resource.validate()

    def read_config(self):
        input_table = InputTable()
        tables_table = TableTable()
        array_table = ArrayTable()
        column_table = ColumnTable()
        if self.input_config_file:
            input_table.from_csv(self.input_config_file)
        if self.tables_config_file:
            tables_table.from_csv(self.tables_config_file)
        if self.arrays_config_file:
            array_table.from_csv(self.arrays_config_file)
        if self.columns_config_file:
            column_table.from_csv(self.columns_config_file)

        if input_table.row_count > 0:
            unique_resources = np.unique(input_table['resource_name'])
            for res_name in unique_resources:
                res_table = input_table.get_rows_by_entries(
                    resource_name=res_name)
                category = str(res_table['category'][0])
                if res_table['type'][0].startswith('H5'):
                    resource = H5Resource(str(res_name),
                                          subfolder='',
                                          category=category,
                                          file_name='')
                    node_names = res_table['subdivision']
                    node_types = res_table['type']
                    for i, node_name in enumerate(node_names):
                        node_type = node_types[i]
                        #read and add rules for arrays
                        if node_type == 'H5Array':
                            node = self.create_H5ArrayNode(res_name,
                                                           node_name,
                                                           array_table)
                        #read and add rules for arrays
                        elif node_type == 'H5Table':
                            node = self.create_H5TableNode(res_name,
                                                           node_name,
                                                           tables_table)
                        resource.add_tables(node)
                    self.add_resources(resource)

    def create_H5ArrayNode(self, res_name, node_name, array_table):
        node = H5Array(node_name)
        if array_table.row_count > 0:
            rows = array_table.get_rows_by_entries(resource_name=res_name,
                                                   subdivision=node_name)
            if rows.row_count > 1:
                raise Exception('{}{} defined more than once in {}'.format(
                    res_name, node_name, self.arrays_config_file))
            if rows.row_count > 0:
                minimum = rows['minimum'][0]
                maximum = rows['maximum'][0]
                dimension = tuple(rows['dimension'][0].split(' x '))
                if len(dimension) == 1:
                    dimension = dimension[0]
                if is_number(minimum):
                    reference = None
                else:
                    reference = self
                min_rule = Rule('min_value', '>=', minimum,
                                reference=reference)
                if is_number(maximum):
                    reference = None
                else:
                    reference = self
                max_rule = Rule('max_value', '<=', maximum,
                                reference=reference)
                dim_rule = Rule('shape', '==', dimension,
                                reference=self)
                node.add_rule(min_rule)
                node.add_rule(max_rule)
                node.add_rule(dim_rule)
        return node

    def create_H5TableNode(self, res_name, node_name, tables_table):
        node = H5Table(node_name)
        if tables_table.row_count > 0:
            rows = tables_table.get_rows_by_entries(
                resource_name=res_name,
                subdivision=node_name)
            if rows.row_count > 0:
                if rows.row_count > 1:
                    raise Exception('{}{} defined more than once in {}'
                                    .format(res_name, node_name,
                                            self.tables_config_file))
                n_rows = rows['n_rows']
                if len(n_rows) == 1:
                    n_rows = n_rows[0]
                dim_rule = Rule('shape', '==', n_rows, reference=self)
                node.add_rule(dim_rule)
        return node


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

class Maxem(TrafficModel):

    DEFAULT_SUBFOLDER = 'Maxem'
    def __init__(self, path=None, parent=None):
        super(Maxem, self).__init__('Maxem')

        self.input_config_file = 'Maxem_input.csv'
        self.tables_config_file = 'Maxem_tables.csv'
        self.arrays_config_file = 'Maxem_arrays.csv'
        self.columns_config_file = 'Maxem_columns.csv'
        self.subfolder = self.DEFAULT_SUBFOLDER
        self.read_config()
        #self.apply_defaults()
        if path is not None:
            self.update()

    @property
    def n_zones(self):
        #number of zones is determined by the number of rows in
        #/zones/zones
        shape = self.resources['Zonen']\
                    .tables['/zones/zones'].shape
        if shape is None:
            return None
        else:
            return shape[0]

    @property
    def n_time_series(self):
        #time series is determined by the number of rows in
        #/activities/time_series
        shape = self.resources['Parameter']\
            .tables['/activities/time_series'].shape
        if shape is None:
            return None
        else:
            return shape[0]

    def apply_defaults(self):
        #### Parameters ####
        params = H5Resource('Parameter',
                            subfolder='params',
                            category='Parameter',
                            file_name='tdm_params.h5')
        time_series = H5Table('/activities/time_series')
        params.add_tables(time_series)

        #### Constants ####
        constants = H5Resource('Konstanten',
                               subfolder='params',
                               category='Parameter',
                               file_name='tdm_constants.h5')

        #### Zonal data ####
        zonal_data = H5Resource('Zonendaten',
                                subfolder='zonal_data',
                                category='Zonen',
                                file_name='zonal_2010_bs_Innenstadt.h5')

        zones = H5Table('/zones/zones')
        rule = Rule('shape', '==', 'n_zones', reference=self)

        access_egress = H5Array('/zones/access_egress')
        binnenreisezeiten = H5Table('/zones/binnenreisezeiten')
        binnenreisezeiten.add_rule(rule)
        production = H5Table('/groups/production')
        production.add_rule(rule)
        activity_kf = H5Table('/activities/activity_kf')
        activity_kf.add_rule(rule)
        attraction = H5Table('/activities/attraction')
        attraction.add_rule(rule)

        zonal_data.add_tables(zones, binnenreisezeiten,
                              access_egress, production,
                              activity_kf, attraction)

        #### Skims #####
        skims_put = H5Resource('SkimsPut',
                               subfolder='matrices\skims_put',
                               category='OV Matrizen',
                               file_name='VEP_NF_final_2010.h5')
        cost_put = H5Array('/put/cost_put')
        rule = Rule('shape', '==', ('n_time_series', 'n_zones', 'n_zones'),
                    reference=self)
        cost_put.add_rule(rule)
        skims_put.add_tables(cost_put)
        self.add_resources(params, constants, zonal_data, skims_put)

    def update(self, path):
        super(Maxem, self).update(path)

    def process(self):
        pass
