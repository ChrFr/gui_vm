from backend import HDF5
import os
import numpy as np


class TrafficModel(object):
    '''
    base class for traffic models
    '''
    def __init__(self, name):
        self.name = name
        #dictionary with categories of resources as keys
        #items are lists of the resources to this category
        self.resources = {}

    def process(self):
        pass

    def set_path(self, path):
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

    def is_complete(self):
        '''
        check if set of resources is complete (all sources are valid)
        '''
        for category in self.resources:
            for resource in self.resources[category]:
                if not resource.is_valid:
                    return False
        return True


class Resource(object):
    '''
    categorized resource for the traffic model calculations

    Parameters
    ----------
    name: String,
          the name of the resource
    category: String, optional
              the category of the resource (e.g. matrices)
    file_name: String, optional
               the name of the resource file
    file_path: String, optional
               the path of the resource file

    '''
    def __init__(self, name, subfolder='', category=None,
                 file_name=None, do_show=True):
        self.name = name
        self.subfolder = subfolder
        self.file_name = file_name
        #category is the folder as it is displayed later
        if do_show:
            if category is None:
                category = self.subfolder
            self.category = category
        self.attributes = {}
        self.validated = {}

    def update(self, path):
        pass

    @property
    def is_set(self):
        if self.file_name is None:
            return False

    @property
    def is_valid(self):
        return False


class H5Resource(Resource):
    '''

    '''
    def __init__(self, name, subfolder='', category=None,
                 file_name=None, do_show=True):
        super(H5Resource, self).__init__(
            name, subfolder=subfolder, category=category,
            file_name=file_name, do_show=do_show)
        self.tables = {}
        #dictionary containing the tables as keys
        #and their attributes as values
        self.attributes = {}
        #dictionary storing the validation messages of the single components
        self.validated = {}

    def add_table(self, table):
        self.tables[table.name] = table

    def validation(self):
        for table in self.tables:
            pass

    def update(self, path):
        '''
        reads and sets the attributes of all set tables

        Parameter
        ---------
        path: String, name of the working directory,
                      where the file is in (without subfolder)
        '''
        h5 = HDF5(os.path.join(path, self.subfolder, self.file_name))
        h5.read()
        for table in self.tables.values():
            table.update(h5)
            self.attributes[table.name] = table.attributes
        del(h5)

    @property
    def is_valid(self):
        for table in tables:
            pass


class H5Table(object):
    def __init__(self, table_path, expected_dtype=None):
            self.name = table_path
            self.table_path = table_path
            self.shape = None
            self.dtype = None
            self.expected_dtype = expected_dtype

    def __repr__(self):
        return 'H5Table {}'.format(self.table_path)

    @property
    def attributes(self):
        return 'Dim {0}'.format(self.shape)

    def update(self, h5_in):
        table = h5_in.get_table(self.table_path).read()
        self.shape = table.shape
        self.dtype = table.dtype

    @property
    def is_valid(self, dimension=None, value_range=None):
        if self.dtype != self.expected_dtype:
            return False


class H5Matrix(object):
    def __init__(self, table_path):
        self.name = table_path
        self.table_path = table_path
        self.shape = None
        self.min_value = None
        self.max_value = None

    def __repr__(self):
        return 'H5Matrix {}'.format(self.table_path)

    @property
    def attributes(self):
        return 'Dimension{}\n Wertebereich [{:.2f} ... {:.2f}]'.format(
            self.shape, self.min_value, self.max_value)

    def update(self, h5_in):
        table = h5_in.get_table(self.table_path).read()
        self.max_value = table.max()
        self.min_value = table.min()
        self.shape = table.shape

    @property
    def is_valid(self, dimension=None, value_range=None):
        pass


