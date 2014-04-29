from backend import HDF5
import os
import numpy as np
import operator as op
import time

OK = 0
NOT_FOUND = 1
MISMATCH = 2
NOT_CHECKED = 3
status_message = ['OK', 'nicht vorhanden', 'falsche Werte', '']

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
    public = {'file_status': 'Datei'}

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
        self.validated = {}
        self.file_status = ''
        self.status_flags = {k: NOT_CHECKED for k, v in self.public.items()}

    def update(self, path):
        file_name = os.path.join(path, self.subfolder, self.file_name)
        if os.path.exists(file_name):
            stats = os.stat(file_name)
            t = time.strftime('%d-%m-%Y %H:%M:%S',
                              time.localtime(stats.st_mtime))
            self.file_status = t
            self.status_flags['file_status'] = OK
        else:
            self.status_flags['file_status'] = NOT_FOUND

    @property
    def attributes(self):
        attributes = {}
        for i, attr in enumerate(self.public):
            value = getattr(self, attr)
            pretty_name = self.public[attr]
            status = self.status_flags[attr]
            message = status_message[status]
            detail = ''
            attr_tuple = (value, detail, message, status)
            attributes[pretty_name] = attr_tuple
        return attributes

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

    @property
    def attributes(self):
        attributes = super(H5Resource, self).attributes
        #add the tables as attributes
        for table in self.tables.values():
            attributes[table.name] = table.attributes
        return attributes

    def add_table(self, table):
        self.tables[table.name] = table
        self.status_flags[table.name] = NOT_CHECKED

    def update(self, path):
        '''
        reads and sets the attributes of all set tables

        Parameter
        ---------
        path: String, name of the working directory,
                      where the file is in (without subfolder)
        '''
        super(H5Resource, self).update(path)
        h5 = HDF5(os.path.join(path, self.subfolder, self.file_name))
        successful = h5.read()
        if not successful:
            #set a flag for file not found
            self.status_flags['file_status'] = NOT_FOUND
        else:
            for table in self.tables.values():
                table.load(h5)
        del(h5)

    def validate(self, path):
        self.update(path)
        if self.status_flags['file_status'] == OK:
            is_valid = True
            for table in self.tables.values():
                if not table.is_valid:
                    is_valid = False
            return is_valid
        return False

#class H5Table(object):
    #def __init__(self, table_path, dtype=None):
        #self.name = table_path
        #self.table_path = table_path
        #self.shape = None
        #self.dtype = None
        #self.expected_dtype = dtype
        #self.error = {}

    #def __repr__(self):
        #return 'H5Table {}'.format(self.table_path)

    #@property
    #def attributes(self):
        #'''
        #attributes returned as a dictionary with
        #representative formatted strings
        #'''
        #attributes = {}
        #dimension = ''
        #for dim in self.shape:
            #dimension += (str(dim) + ' x ')
        #dimension = dimension[:-3]
        #attributes['Reihen'] = dimension
        #return attributes, self.error

    #def load(self, h5_in):
        #table = h5_in.get_table(self.table_path).read()
        #self.shape = table.shape
        #self.dtype = table.dtype

    #@property
    #def is_valid(self, dimension=None, value_range=None):
        #if self.dtype != self.expected_dtype:
            #return (False, 'Spalte fehlt')
        #return True


class H5Matrix(object):
    public = {'shape': 'Dimension',
              'min_value': 'Minimalwert',
              'max_value': 'Maximalwert'}

    def __init__(self, table_path):
        self.name = table_path
        self.table_path = table_path
        self.shape = None
        self.min_value = None
        self.max_value = None
        self.rules = []
        #set flags to not checked
        self.status_flags = {k: NOT_CHECKED for k, v in self.public.items()}

    def __repr__(self):
        return 'H5Table {}'.format(self.table_path)

    @property
    def attributes(self):
        '''
        dictionary with pretty attributes as keys and representative
        formatted strings of the actual and the target values of those
        attributes (target only if error occured, else empty string)

        Return
        ------
        attributes: dict,
                    attribute names as keys
                    (actual value, message, errorflag) as values
        '''
        attributes = {}
        error = {}
        expected = {}
        for rule in self.rules:
            expected[rule.field_name] = rule.value
        for i, attr in enumerate(self.public):
            value = getattr(self, attr)
            pretty_name = self.public[attr]
            status = self.status_flags[attr]
            message = status_message[status]
            if expected.has_key(attr):
                target = expected[attr]
            else:
                target = ''
            attr_tuple = (value, target, message, status)
            attributes[pretty_name] = attr_tuple
        return attributes

    def load(self, h5_in):
        table = h5_in.get_table(self.table_path).read()
        self.max_value = table.max()
        self.min_value = table.min()
        self.shape = table.shape

    def add_rules(self, **kwargs):
        reference = None
        if 'operator' not in kwargs:
            raise Exception('Missing argument: operator=...')
        else:
            operator = kwargs.pop('operator')
        if 'reference' in kwargs:
            reference = kwargs.pop('reference')
        for name, value in kwargs.items():
            rule = Rule(name, value, operator, reference=reference)
            self.rules.append(rule)

    def add_rule(self, field_name, value, operator, reference=None):
        rule = Rule(field_name, value, operator, reference=reference)
        self.rules.append(rule)


    #def add_rule(self, reference=None, shape=None,
                       #max_value=None, min_value=None):
        #if shape is not None:
            #if reference is not None:
                #self.expected_shape = (reference, shape)
            #else:
                #self.expected_shape = shape

    @property
    def is_valid(self):
        is_valid = True
        for rule in self.rules:
            if not rule.check(self):
                is_valid = False
                self.status_flags[rule.field_name] = MISMATCH
            else:
                self.status_flags[rule.field_name] = OK
        return is_valid

class Rule(object):
    wildcards = ['*', '']
    mapping = {'>': op.gt,
               '>=': op.ge,
               '=>': op.ge,
               '<': op.lt,
               '=<': op.le,
               '<=': op.le,
               '==': op.eq,
               '!=': op.ne,
               }

    def __init__(self, field_name, value, operator, reference=None):
        self.reference = reference
        self.operator = operator
        self.field_name = field_name
        self._value = value

    @property
    def value(self):
        value = list(self._value)
        for i, val in enumerate(self._value):
            #ignore wildcards
            if val in self.wildcards:
                continue
            if isinstance(val, str):
                #look if the referenced object has a field with the name
                if (self.reference is not None) and \
                   hasattr(self.reference, val):
                    value[i] = getattr(self.reference, val)
        return tuple(value)

    def check(self, obj):
        message = None
        is_valid = True
        #map the operator string to its function
        compare = self.mapping[self.operator]

        #get the field of the object
        if not hasattr(obj, self.field_name):
            raise Exception('The object {} does not own a field {}'
                            .format(obj, self.field_name))
        attr = getattr(obj, self.field_name)
        #wrap all values with a list (if they are not already)
        if (not isinstance(attr, list)) and (not isinstance(attr, tuple)):
            attr = [attr]
        value = self.value
        if (not isinstance(value, list)) and (not isinstance(value, tuple)):
            value = [value]
        if len(attr) != len(value):
            return False
        #compare the field of the given object with the defined value
        for i, val in enumerate(value):
            #ignore wildcards
            if val in self.wildcards:
                continue
            #compare the value with the field of the given object
            if not compare(attr[i], val):
                is_valid = False
        return is_valid
