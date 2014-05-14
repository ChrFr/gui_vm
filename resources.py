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

DEFAULT_MESSAGES = ['', 'gefunden', 'ueberprueft',
                    'nicht gefunden', 'Fehler']


class Resource(object):
    '''
    base class for resource files and their subdivisions
    '''
    #dictionary for monitored attributes
    monitored = OrderedDict()

    def __init__(self, name):
        self.name = name
        self.children = []
        self.rules = []
        self.overall_status = NOT_CHECKED
        #add status flags for the monitored attributes
        self.status_flags = {k: NOT_CHECKED for k, v in self.monitored.items()}

    def add_child(self, child):
        self.children.append(child)
        self.status_flags[child.name] = NOT_CHECKED

    def get_child(self, name):
        for child in self.children:
            if child.name == name:
                return child
        return None

    def add_rule(self, rule):
        self.rules.append(rule)

    def update(self, path):
        self.clear_status()
        for child in self.children:
            child.update(path)
        self.set_overall_status()

    def set_overall_status(self):
        status = NOT_CHECKED
        for flag in self.status_flags.values():
            if isinstance(flag, tuple):
                flag = flag[0]
            if flag > status:
                status = flag
        for child in self.children:
            child.set_overall_status()
            child_status = child.overall_status
            if child_status > status:
                status = child_status
        self.overall_status = status

    @property
    def status(self, overwrite=None):
        '''
        dictionary with pretty attributes as keys and a tuple as values
        with the actual value, a message and a status flag

        Return
        ------
        attributes: dict,
                    attribute names as keys
                    (name of attribute, message, statusflag) as values
        '''

        status = OrderedDict()
        attributes = OrderedDict()
        #add the status of the monitored attributes
        for i, attr in enumerate(self.monitored):
            value = getattr(self, attr)
            pretty_name = self.monitored[attr]
            status_flag = self.status_flags[attr]
            if isinstance(status_flag, tuple):
                message = status_flag[1]
                status_flag = status_flag[0]
            else:
                message = DEFAULT_MESSAGES[status_flag]
            attr_tuple = (value, message, status_flag)
            attributes[pretty_name] = attr_tuple
        #add the status of the children
        for child in self.children:
            attributes.update(child.status)  #, '', child.overall_status)
        status[self.name] = (attributes, DEFAULT_MESSAGES[self.overall_status],
                             self.overall_status)
        return status

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

    def validate(self, path):
        self.update(path)
        #only check rules if successfully loaded, removed
        if self.overall_status != NOT_FOUND:
            self._validate(path)
        self.set_overall_status()

    def _validate(self, path):
        for rule in self.rules:
            if not rule.check(self):
                is_valid = False
                self.status_flags[rule.field_name] = MISMATCH
            else:
                self.status_flags[rule.field_name] = CHECKED_AND_VALID
        for child in self.children:
            child._validate(path)

    def clear_status(self):
        self.overall_status = NOT_CHECKED
        self.status_flags = {k: NOT_CHECKED for k, v in self.monitored.items()}
        for child in self.children:
            child.clear_status()



class ResourceFile(Resource):
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
    monitored = OrderedDict([('file_name', 'Datei'),
                             ('file_modified', 'Datum')])

    def __init__(self, name, subfolder='', category=None,
                 file_name=None, do_show=True):
        self.monitored.update(super(ResourceFile, self).monitored)
        super(ResourceFile, self).__init__(name)
        self.subfolder = subfolder
        self.file_name = file_name
        #category is the folder as it is displayed later
        if do_show:
            if category is None:
                category = self.subfolder
            self.category = category
        self.file_modified = ''

    def set_source(self, file_name, subfolder):
        self.file_name = file_name
        self.subfolder = subfolder

    def update(self, path):
        '''
        base class only checks if file exists, actual reading has to be done
        in the subclasses
        '''
        self.clear_status()
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
    def is_set(self):
        if self.file_name is None:
            return False


class H5Resource(ResourceFile):
    '''

    '''
    def __init__(self, name, subfolder='', category=None,
                 file_name=None, do_show=True):
        super(H5Resource, self).__init__(
            name, subfolder=subfolder, category=category,
            file_name=file_name, do_show=do_show)

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
            self.status_flags['file_name'] = (MISMATCH,
                                              'keine gueltige HDF5 Datei')
        else:
            #give child tables the opened h5 file
            #to avoid multiple readings of the same file
            for child in self.children:
                child.update(h5)
        self.set_overall_status()
        #close file
        del(h5)


class H5Node(Resource):
    monitored = OrderedDict([('table_path', 'Pfad'),
                             ('shape', 'Dimension')])

    def __init__(self, table_path):
        name = os.path.split(table_path)[1]
        super(H5Node, self).__init__(name)
        self.table_path = table_path
        self.shape = None
        #set flags to not checked
        self.status_flags = {k: NOT_CHECKED for k, v in self.monitored.items()}

    def __repr__(self):
        return 'H5Node {}'.format(self.table_path)

    def update(self, h5_in):
        table = h5_in.get_table(self.table_path)
        if not table:
            self.status_flags['table_path'] = NOT_FOUND
            return None
        self.status_flags['table_path'] = FOUND
        table = table.read()
        self.shape = table.shape
        return table

    @property
    def status(self):
        status = super(H5Node, self).status
        #pretty print the dimension (instead of tuple (a, b, c) 'a x b x c')
        if self.shape is not None:
            dim = ''
            for v in self.shape:
                dim += '{} x '.format(v)
            dim = dim[:-3]
            dim_status = list(status[self.name][0][self.monitored['shape']])
            dim_status[0] = dim
            status[self.name][0][self.monitored['shape']] = tuple(dim_status)
        return status

class H5Table(H5Node):
    monitored = OrderedDict()

    def __init__(self, table_path):
        #set dict for monitored attributes, then call super constructor
        #(there the flags are built out of monitored dict)
        self.monitored.update(super(H5Table, self).monitored)
        self.monitored['shape'] = 'Reihen'
        super(H5Table, self).__init__(table_path)

    def __repr__(self):
        return 'H5Table {}'.format(self.table_path)

    def update(self, h5_in):
        table = super(H5Table, self).update(h5_in)
        if table is not None:
            for child in self.children:
                child.update(table)

    @property
    def column_names(self):
        column_names = []
        for col in self.children:
            col_names.append(col.name)
        return column_names


class H5TableColumn(Resource):
    '''

    Parameter
    ---------

    track_content: bool, optional
                   if True the content of the table will be saved in the
                   attribute self.content with every update
    '''
    monitored = OrderedDict([('dtype', 'dtype'),
                             ('primary_key', 'Primaerschluessel'),
                             ('max_value', 'Maximum'),
                             ('min_value', 'Minimum')])

    def __init__(self, name, primary_key=False, track_content=False):
        super(H5TableColumn, self).__init__(name)
        self.max_value = None
        self.min_value = None
        self.primary_key = primary_key
        self.dtype = None
        self.track_content = track_content
        self.content = None

    def update(self, table):
        if self.name not in table.dtype.names:
            self.status_flags['dtype'] = NOT_FOUND
        else:
            self.dtype = table.dtype[self.name]
            self.status_flags['dtype'] = FOUND
            col = table[self.name]
            if self.dtype.char != 'S':
                self.max_value = col.max()
                self.min_value = col.min()
            #check if all values are unique if primary key
            if self.primary_key and np.unique(col).size != col.size:
                self.status_flags['primary_key'] = (MISMATCH,
                                                    'Werte nicht eindeutig')
            if self.track_content:
                self.content = list(col)

class H5Array(H5Node):
    monitored = OrderedDict([('min_value', 'Minimalwert'),
                             ('max_value', 'Maximalwert')])

    def __init__(self, table_path):
        #set dict for monitored attributes, then call super constructor
        #(there the flags are built out of monitored dict)
        #copy and update needed here to keep order
        d = copy.copy(super(H5Array, self).monitored)
        d.update(self.monitored)
        self.monitored = d
        super(H5Array, self).__init__(table_path)
        self.min_value = None
        self.max_value = None

    def __repr__(self):
        return 'H5Matrix {}'.format(self.table_path)

    def update(self, h5_in):
        table = super(H5Array, self).update(h5_in)
        if table is not None:
            self.max_value = table.max()
            self.min_value = table.min()

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
                #check again if value is number in string
                if isinstance(val, str) and is_number(val):
                    val = float(val)
                if not compare(attr[i], val):
                    is_valid = False
        return is_valid
