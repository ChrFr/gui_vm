from backend import HDF5
import os
import numpy as np
import operator as op
import time

#status flags (with ascending priority)
NOT_CHECKED = 0
FOUND = 1
CHECKED = 2
NOT_FOUND = 3
MISMATCH = 4


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

    @property
    def overall_status(self):
        status = NOT_CHECKED
        for flag in self.status_flags.values():
            if flag > status:
                status = flag
        return status


    def update(self, path):
        file_name = os.path.join(path, self.subfolder, self.file_name)
        if os.path.exists(file_name):
            stats = os.stat(file_name)
            t = time.strftime('%d-%m-%Y %H:%M:%S',
                              time.localtime(stats.st_mtime))
            self.file_status = t
            self.status_flags['file_status'] = FOUND
        else:
            self.status_flags['file_status'] = NOT_FOUND

    @property
    def attributes(self):
        '''
        dictionary with pretty attributes as keys and a tuple as values
        with the actual value, a message and a status flag

        Return
        ------
        attributes: dict,
                    attribute names as keys
                    (actual value, message, statusflag) as values
        '''
        attributes = {}
        attr_dict = {}
        for i, attr in enumerate(self.public):
            value = getattr(self, attr)
            pretty_name = self.public[attr]
            status = self.status_flags[attr]
            detail = ''
            attr_tuple = (value, detail, status)
            attr_dict[pretty_name] = attr_tuple
        attributes[self.name] = (attr_dict, '', self.overall_status)
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
    def overall_status(self):
        status = super(H5Resource, self).overall_status
        #check all tables additionally
        for table in self.tables.values():
            flag = table.overall_status
            if flag > status:
                status = flag
        return status

    @property
    def attributes(self):
        attributes = super(H5Resource, self).attributes
        #add the tables as attributes
        attr_dict = {}
        for table in self.tables.values():
            attr_dict[table.name] = table.attributes
        attributes[self.name][0].update(attr_dict)
        return attributes

    def add_tables(self, *args):
        for table in args:
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
        if self.status_flags['file_status'] == FOUND:
            is_valid = True
            for table in self.tables.values():
                if not table.is_valid:
                    is_valid = False
            return is_valid
        return False


class H5Node(object):
    public = {'shape': 'Dimension'}

    def __init__(self, table_path):
        self.name = table_path
        self.table_path = table_path
        self.shape = None
        self.rules = []
        #set flags to not checked
        self.status_flags = {k: NOT_CHECKED for k, v in self.public.items()}

    def __repr__(self):
        return 'H5Node {}'.format(self.table_path)

    @property
    def overall_status(self):
        status = NOT_CHECKED
        for flag in self.status_flags.values():
            if flag > status:
                status = flag
        return status

    @property
    def attributes(self):
        '''
        dictionary with pretty attributes as keys and a tuple as values
        with the actual and the target values of those attributes
        and a status flag

        Return
        ------
        attributes: dict,
                    attribute names as keys
                    (actual value, target, statusflag) as values
        '''
        attributes = {}
        expected = {}
        for rule in self.rules:
            expected[rule.field_name] = rule.value
        for i, attr in enumerate(self.public):
            value = getattr(self, attr)
            pretty_name = self.public[attr]
            status = self.status_flags[attr]
            if expected.has_key(attr):
                target = expected[attr]
            else:
                target = ''
            attr_tuple = (value, target, status)
            attributes[pretty_name] = attr_tuple
        return (attributes, '', self.overall_status)

    def load(self, h5_in):
        table = h5_in.get_table(self.table_path).read()
        self.shape = table.shape

    def define_rules(self, **kwargs):
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

    def add_rule(self, rule):
        self.rules.append(rule)

    @property
    def is_valid(self):
        is_valid = True
        for rule in self.rules:
            if not rule.check(self):
                is_valid = False
                self.status_flags[rule.field_name] = MISMATCH
            else:
                self.status_flags[rule.field_name] = CHECKED
        return is_valid


class H5Table(H5Node):
    public = {}

    def __init__(self, table_path):
        #set dict for public attributes, then call super constructor
        #(there the flags are built out of public dict)
        self.public.update(super(H5Table, self).public)
        super(H5Table, self).__init__(table_path)

    def __repr__(self):
        return 'H5Table {}'.format(self.table_path)

    def load(self, h5_in):
        table = h5_in.get_table(self.table_path).read()
        self.shape = table.shape


class H5Matrix(H5Node):
    public = {'min_value': 'Minimalwert',
              'max_value': 'Maximalwert'}

    def __init__(self, table_path):
        #set dict for public attributes, then call super constructor
        #(there the flags are built out of public dict)
        self.public.update(super(H5Matrix, self).public)
        super(H5Matrix, self).__init__(table_path)
        self.min_value = None
        self.max_value = None

    def __repr__(self):
        return 'H5Matrix {}'.format(self.table_path)

    def load(self, h5_in):
        table = h5_in.get_table(self.table_path).read()
        self.max_value = table.max()
        self.min_value = table.min()
        self.shape = table.shape


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

    def __init__(self, field_name, operator, value, reference=None):
        self.reference = reference
        self.operator = operator
        self.field_name = field_name
        self._value = value

    @property
    def value(self):
        value = self._value
        if (not isinstance(value, list)) and (not isinstance(value, tuple)):
            value = [value]
        for i, val in enumerate(value):
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
        is_valid = True
        #map the operator string to its function
        compare = self.mapping[self.operator]

        #get the field of the object
        if not hasattr(obj, self.field_name):
            raise Exception('The object {} does not own a field {}'
                            .format(obj, self.field_name))
        attr = getattr(obj, self.field_name)
        #wrap all values with a list (if they are not already)
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
