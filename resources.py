from backend import HDF5
import os
import numpy as np
import operator as op
import time
from collections import OrderedDict
import copy

#status flags (with ascending priority)
NOT_CHECKED = 0
FOUND = 1
CHECKED_AND_VALID = 2
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
    public = OrderedDict([('file_name', 'Datei'),
                          ('file_modified', 'Datum')])

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
        self.file_modified = ''
        self.status_flags = {k: NOT_CHECKED for k, v in self.public.items()}

    @property
    def overall_status(self):
        status = NOT_CHECKED
        for flag in self.status_flags.values():
            if flag > status:
                status = flag
        return status

    def set_source(self, file_name, subfolder):
        self.file_name = file_name
        self.subfolder = subfolder

    def update(self, path):
        '''
        base class only checks if file exists, actual reading has to be done
        in the subclasses
        '''
        if self.file_name != '':
            file_name = os.path.join(path, self.subfolder, self.file_name)
            if os.path.exists(file_name):
                stats = os.stat(file_name)
                t = time.strftime('%d-%m-%Y %H:%M:%S',
                                  time.localtime(stats.st_mtime))
                self.file_modified = t
                self.status_flags['file_name'] = FOUND
                return
        self.status_flags['file_name'] = NOT_FOUND

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
        attributes = OrderedDict()
        attr_dict = OrderedDict()
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
    def is_checked(self):
        if self.overall_status > 1:
            return True
        else:
            return False

    @property
    def is_valid(self):
        if self.overall_status == 2:
            return True
        else:
            return False


class H5Resource(Resource):
    '''

    '''
    def __init__(self, name, subfolder='', category=None,
                 file_name=None, do_show=True):
        super(H5Resource, self).__init__(
            name, subfolder=subfolder, category=category,
            file_name=file_name, do_show=do_show)
        self.tables = OrderedDict()

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
        attr_dict = OrderedDict()
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
            self.status_flags['file_name'] = NOT_FOUND
        else:
            for table in self.tables.values():
                table_read = table.load(h5)
                if table_read:
                    self.status_flags[table.name] = FOUND
                else:
                    self.status_flags[table.name] = NOT_FOUND
        del(h5)

    def validate(self, path):
        self.update(path)
        if self.status_flags['file_name'] == FOUND:
            is_valid = True
            for table in self.tables.values():
                if not table.is_valid:
                    is_valid = False
            return is_valid
        return False


class H5Node(object):
    public = OrderedDict([('shape', 'Dimension')])

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
        attributes = OrderedDict()
        expected = OrderedDict()
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
            if attr == 'shape' and value is not None:
                dim = ''
                for v in value:
                    dim += '{} x '.format(v)
                value = dim[:-3]
            attr_tuple = (value, target, status)
            attributes[pretty_name] = attr_tuple
        return (attributes, '', self.overall_status)

    def load(self, h5_in):
        table = h5_in.get_table(self.table_path)
        if not table:
            return False
        table = table.read()
        self.shape = table.shape
        return True

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
                self.status_flags[rule.field_name] = CHECKED_AND_VALID
        return is_valid


class H5Table(H5Node):
    public = OrderedDict()

    def __init__(self, table_path, dtype=None):
        #set dict for public attributes, then call super constructor
        #(there the flags are built out of public dict)
        self.public.update(super(H5Table, self).public)
        self.public['shape'] = 'Reihen'
        super(H5Table, self).__init__(table_path)
        self.dtype = dtype
        self.columns = []

    def __repr__(self):
        return 'H5Table {}'.format(self.table_path)

    def load(self, h5_in):
        table = h5_in.get_table(self.table_path)
        if not table:
            return False
        table = table.read()
        self.shape = table.shape
        for col_name in table.dtype.names:
            dtype = table.dtype[col_name]
            col = H5TableColumn(col_name, dtype=dtype)
            #no max or min for strings
            if dtype.char != 'S':
                col.max_value = table[col_name].max()
                col.min_value = table[col_name].min()
            self.columns.append(col)
        return True
    @property
    def column_names(self):
        column_names = []
        for col in self.columns:
            column_names.append(col.name)
        return column_names

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
        attributes = super(H5Table, self).attributes[0]
        #add the tables as attributes
        attr_dict = OrderedDict()
        for col in self.columns:
            attr_dict[col.name] = col.attributes
        attributes.update(attr_dict)
        return (attributes, '', self.overall_status)


class H5TableColumn(H5Node):
    public = OrderedDict([('primary_key', 'Primaerschluessel'),
                          ('dtype', 'dtype'),
                          ('max_value', 'Maximum'),
                          ('min_value', 'Minimum')])

    def __init__(self, name, primary_key=False, dtype=None):
        super(H5TableColumn, self).__init__(name)
        self.max_value = None
        self.min_value = None
        self.primary_key = primary_key
        self.dtype = dtype
        self.rules = []


class H5Array(H5Node):
    public = OrderedDict([('min_value', 'Minimalwert'),
                          ('max_value', 'Maximalwert')])

    def __init__(self, table_path):
        #set dict for public attributes, then call super constructor
        #(there the flags are built out of public dict)
        self.public.update(super(H5Array, self).public)
        super(H5Array, self).__init__(table_path)
        self.min_value = None
        self.max_value = None

    def __repr__(self):
        return 'H5Matrix {}'.format(self.table_path)

    def load(self, h5_in):
        table = h5_in.get_table(self.table_path)
        if not table:
            return False
        table = table.read()
        self.max_value = table.max()
        self.min_value = table.min()
        shape = list(table.shape)
        #get rid of the L's
        for i, dim in enumerate(shape):
            shape[i] = int(dim)
        self.shape = tuple(shape)
        return True

class Rule(object):
    def check(self, obj):
        return True

class DtypeRule(object):
    pass


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def is_in_list(self, left_list, right_list):
        '''
        check if all elements of left list are in right list
        '''
        if not isinstance(left_list, list):
            left_list = [left_list]
        if not isinstance(right_list, list):
            right_list = [right_list]
        for element in left_list:
            if element not in right_list:
                return False
        return True

class CompareRule(Rule):
    wildcards = ['*', '']
    mapping = {'>': op.gt,
               '>=': op.ge,
               '=>': op.ge,
               '<': op.lt,
               '=<': op.le,
               '<=': op.le,
               '==': op.eq,
               '!=': op.ne,
               'in': is_in_list,
               }

    def __init__(self, field_name, operator, value, reference=None):
        self.reference = reference
        self.operator = operator
        self.field_name = field_name
        if isinstance(value, str) and is_number(value):
            value = float(value)
            if value % 1 == 0:
                value = int(value)
        self._value = value

    @property
    def value(self):
        '''
        if referenced:
        get the fields from the referenced object and return it's value
        '''
        #copy needed (otherwise side effect is caused)
        value = copy.copy(self._value)
        if self.reference:
            cast = False
            if isinstance(value, tuple):
                value = list(value)
                cast = True
            if (not isinstance(value, list)):
                value = [value]
                cast = True
            for i, val in enumerate(value):
                #ignore wildcards
                if val in self.wildcards:
                    continue
                if isinstance(val, str):
                    #look if the referenced object has a field with the name
                    if (self.reference is not None) and \
                       hasattr(self.reference, val):
                        attr = getattr(self.reference, val)
                        if attr is not None:
                            attr = int(attr)
                        value[i] = attr
            if cast:
                value = tuple(value)
        return value

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
        if (not isinstance(attr, list)) and (not isinstance(attr, tuple)):
            attr = [attr]
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
