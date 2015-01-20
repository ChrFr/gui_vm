# -*- coding: utf-8 -*-
from backend import HDF5
import os
import numpy as np
import operator as op
import time
from collections import OrderedDict
from gui_vm.model.observable import Observable
import copy

#status flags (with ascending priority)
NOT_CHECKED = 0
FOUND = 1
CHECKED_AND_VALID = 2
NOT_FOUND = 3
MISMATCH = 4

DEFAULT_MESSAGES = ['', 'vorhanden', 'überprüft',
                    'nicht vorhanden', 'Fehler']


class Resource(Observable):
    '''
    base class for resource files and their subdivisions, may have further
    subdivisions of this resource as children

    important: represents the target resources as needed by the traffic models,
    actual status will be verified by updating and validating all resources

    Parameter
    ---------
    name: String, the name this resource gets
    '''
    #dictionary for monitored attributes
    monitored = OrderedDict()

    def __init__(self, name):
        super(Resource, self).__init__()
        self.name = name
        self.children = []
        self.rules = []
        self.required = False
        self.dynamic = False
        self.overall_status = NOT_CHECKED, []
        #add status flags for the monitored attributes
        self.status_flags = {k: (NOT_CHECKED, DEFAULT_MESSAGES[NOT_CHECKED])
                             for k, v in self.monitored.items()}

    def get(self, path, content_path):
        return None

    def add_child(self, child):
        '''
        add a child resource
        '''
        self.children.append(child)
        self.status_flags[child.name] = (NOT_CHECKED,
                                         DEFAULT_MESSAGES[NOT_CHECKED])

    def get_child(self, name):
        '''
        get a child resource by name, return None if not found
        '''
        for child in self.children:
            if child.name == name:
                return child
        return None

    def add_rule(self, rule):
        '''
        add a rule to this resource
        '''
        self.rules.append(rule)

    def update(self, path):
        '''
        update the resource and all of its children recursive
        in the given project path
        '''
        self.clear_status()
        self.reset()
        for child in self.children:
            child.update(path)
        self.set_overall_status()

    def set_overall_status(self):
        '''
        calculate and set the status of this resource by checking the
        status of its children, the highest status will be taken
        (ascending hierarchical order of status)
        '''
        status_flag = NOT_CHECKED
        messages = []
        for flag in self.status_flags.values():
            if not isinstance(flag, tuple):
                flag = (flag, DEFAULT_MESSAGES[flag])
            msg = flag[1]
            if len(msg) > 0 and msg not in messages:
                messages.append(msg)
            if flag[0] > status_flag:
                status_flag = flag[0]
        for child in self.children:
            child.set_overall_status()
            child_status = child.overall_status[0]
            child_msgs = child.overall_status[1]
            for child_msg in child_msgs:
                if len(child_msg) > 0 and child_msg not in messages:
                    messages.append(child_msg)
            if child_status > status_flag:
                status_flag = child_status
        self.overall_status = status_flag, messages

    @property
    def status(self, overwrite=None):
        '''
        dictionary with pretty attributes as keys and a tuple as values
        with the actual value, a message and a status flag
        can be nested if there are child resources, their status will
        appear instead of the message

        Return
        ------
        attributes: dict,
                    attribute names as keys, tuple (name of attribute, message
                    or child status, statusflag) as values
        '''

        status = OrderedDict()
        attributes = OrderedDict()
        #add the status of the monitored attributes
        for i, attr in enumerate(self.monitored):
            target = getattr(self, attr)
            pretty_name = self.monitored[attr]
            status_flag = self.status_flags[attr]
            if isinstance(status_flag, tuple):
                message = status_flag[1]
                status_flag = status_flag[0]
            else:
                message = DEFAULT_MESSAGES[status_flag]
            attr_tuple = (target, message, status_flag)
            attributes[pretty_name] = attr_tuple
        #add the status of the children
        for child in self.children:
            attributes.update(child.status)
        status[self.name] = (attributes, ', '.join(self.overall_status[1]),
                             self.overall_status[0])
        return status

    @property
    def is_checked(self):
        if self.overall_status[0] > 1:
            return True
        else:
            return False

    @property
    def is_valid(self):
        if self.overall_status[0] == 2:
            return True
        else:
            return False

    def read(self, path):
        return None, False

    def validate(self, path):
        '''
        validate the resource and set the status
        '''
        self.update(path)
        #only check rules if successfully loaded, removed
        if self.overall_status[0] != NOT_FOUND:
            self._validate(path)
        self.set_overall_status()

    def _validate(self, path):
        '''
        recursive validation of the children by checking the rules,
        set the status according to the results of the check of the rules
        '''
        for rule in self.rules:
            is_valid, message = rule.check(self)
            if not is_valid:
                self.status_flags[rule.field_name] = (MISMATCH, message)
            else:
                self.status_flags[rule.field_name] = (CHECKED_AND_VALID,
                                                      message)
        for child in self.children:
            child._validate(path)

    def clear_status(self):
        '''
        reset the status flags of the resource and its children recursive
        '''
        self.overall_status = NOT_CHECKED
        self.status_flags = {k: (NOT_CHECKED, DEFAULT_MESSAGES[NOT_CHECKED])
                             for k, v in self.monitored.items()}
        for child in self.children:
            child.clear_status()

    def remove_children(self):
        if len(self.children) > 0:
            for i in xrange(len(self.children)):
                self.children.pop(0).remove_children()


class ResourceFile(Resource):
    '''
    categorized resource for the traffic model calculations

    Parameters
    ----------
    name: String,
          the name of the resource
    category: String, optional
              the category of the resource (e.g. matrices)
    subfolder: String, optional
               the subfolder the file is in
    filename: String, optional
               the name of the resource file
    file_path: String, optional
               the path of the resource file

    '''
    monitored = OrderedDict([('filename', 'Datei'),
                             ('file_modified', 'Datum')])

    def __init__(self, name, subfolder='', filename=None):
        self.monitored.update(super(ResourceFile, self).monitored)
        super(ResourceFile, self).__init__(name)
        self.subfolder = subfolder
        self.filename = filename
        self.file_modified = ''

    def set_source(self, filename, subfolder=None):
        '''
        set the filename and the subpath of the resource
        '''
        self.filename = filename
        if subfolder is not None:
            self.subfolder = subfolder

    def update(self, path):
        '''
        base class only checks if file exists, actual reading has to be done
        in the subclasses
        '''
        self.reset()
        self.clear_status()
        if self.filename != '' and self.filename is not None:
            filename = os.path.join(path, self.subfolder, self.filename)
            if os.path.exists(filename):
                stats = os.stat(filename)
                t = time.strftime('%d-%m-%Y %H:%M:%S',
                                  time.localtime(stats.st_mtime))
                self.file_modified = t
                self.status_flags['filename'] = FOUND
                return
        self.status_flags['filename'] = NOT_FOUND

    @property
    def is_set(self):
        if self.filename is None:
            return False

    def set_overall_status(self):
        #don't show all child messages for resource files (confusing)
        super(ResourceFile, self).set_overall_status()
        status_flag = self.overall_status[0]
        self.overall_status = status_flag, [DEFAULT_MESSAGES[status_flag]]


class H5Resource(ResourceFile):
    '''
    Resource holding information about a HDF5 resource file

    Parameters
    ----------
    name: String,
          the name the resource gets
    subfolder: String, optional
               the subfolder the file is in
    category: String, optional
              the category of the resource (e.g. matrices)
    filename: String, optional
               the name of the h5 resource file
    '''
    def __init__(self, name, subfolder='',
                 filename=None):
        super(H5Resource, self).__init__(
            name, subfolder=subfolder,
            filename=filename)

    def read(self, path):
        h5 = HDF5(os.path.join(path, self.subfolder, self.filename))
        successful = h5.read()
        return h5, successful

    def get_content(self, path, content_path):
        h5, success = self.read(path)
        if not success:
            return None
        return h5.get_table(content_path).read()

    def update(self, path):
        '''
        reads and sets the attributes of all child nodes

        Parameter
        ---------
        path: String, name of the working directory,
                      where the file is in (without subfolder)
        '''
        super(H5Resource, self).update(path)
        h5_in = None
        #reset contents
        self._content = {}
        if self.status_flags['filename'] == FOUND:
            h5_in, success = self.read(path)
            if not success:
                #set a flag for file not found
                self.status_flags['filename'] = (NOT_FOUND,
                                                 'keine gueltige HDF5 Datei')
            for child in self.children:
                child.update(path, h5_in=h5_in)
        #close file
        del(h5_in)
        self.set_overall_status()


class H5Node(H5Resource):
    '''
    Resource holding information about a node inside HDF5 resource file

    Parameter
    ---------
    table_path: path of the table inside the h5 file
    '''
    monitored = OrderedDict([('table_path', 'Pfad'),
                             ('shape', 'Dimension')])

    def __init__(self, table_path):
        #name = os.path.split(table_path)[1]
        super(H5Node, self).__init__(table_path)
        self.table_path = table_path
        self.shape = None
        #set flags to not checked
        self.status_flags = {k: NOT_CHECKED for k, v in self.monitored.items()}

    def __repr__(self):
        return "H5Node {} - {}".format(self.name, self.table_path)

    def read(self, path, h5_in=None):
        if not h5_in:
            h5_in, success = super(H5Node, self).read(path)
            if not success:
                return None
        table = h5_in.get_table(self.table_path)
        if not table:
            return None
        return table

    def update(self, path, h5_in = None):
        '''
        read and set the attributes of this node

        Parameter
        ---------
        path: String, name of the working directory,
                      where the file is in (without subfolder)
        '''
        self.reset()
        table = self.read(path, h5_in=h5_in)
        if not table:
            self.status_flags['table_path'] = NOT_FOUND
            self.shape = None
            return None
        self.status_flags['table_path'] = FOUND
        table = table.read()
        self.shape = table.shape
        return table

    @property
    def status(self):
        '''
        adds a pretty representation of the dimension to the status gotten from
        the base class
        '''
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
    '''
    Resource holding information about a table inside a HDF5 resource file

    Parameter
    ---------
    table_path: path of the table inside the h5 file
    '''
    #monitored = OrderedDict([('column_names', 'benötigte Spalten')])

    def __init__(self, table_path):
        #set dict for monitored attributes, then call super constructor
        #(there the flags are built out of monitored dict)
        self.monitored.update(super(H5Table, self).monitored)
        self.monitored['shape'] = 'Reihen'
        self._required_columns = []
        super(H5Table, self).__init__(table_path)

    def __repr__(self):
        return "H5Table {} - {}".format(self.name, self.table_path)

    def update(self, path, h5_in = None):
        '''
        set the table to the given h5

        Parameter
        ---------
        h5_in: HDF5, opened hdf5 file containing this table
        '''
        #clear extra columns, only keep those that are required by definition
        tmp = []
        for i in xrange(len(self.children)):
            child = self.children.pop(0)
            if not child.required:
                child.remove_children()
            else:
                child.reset()
                tmp.append(child)
        self.children = tmp
        table = super(H5Table, self).update(path, h5_in=h5_in)
        if table is None:
            return
        #add extra columns inside the given h5 (not required ones)
        col_names = self.column_names
        for existing_col in table.dtype.names:
            if existing_col not in self.column_names:
                col = H5TableColumn(existing_col)
                self.add_child(col)

        for child in self.children:
            child.update(table)

    @property
    def column_names(self):
        '''
        return the names of all child columns
        '''
        column_names = []
        for col in self.children:
            column_names.append(col.name)
        return column_names


class H5TableColumn(H5Resource):
    '''
    Resource holding information about a table inside a HDF5 resource file

    Parameter
    ---------
    name:           the name the column gets
    dtype:          String, optional
                    expected dtype
    minimum:        String, optional
                    expected minimum
    maximum:        String, optional
                    expected maximum
    is_primary_key: bool, optional
                    is the column expected to contain primary keys
    reference:      object, optional
                    a referenced object, by name referenced minima or maxima are
                    are taken from this object
    required:       bool, optional
                    determines, if the column is required by the traffic model
    '''
    monitored = OrderedDict([('dtype', 'dtype'),
                             ('primary_key', 'Primaerschluessel'),
                             ('max_value', 'Maximum'),
                             ('min_value', 'Minimum')])

    def __init__(self, name, primary_key=False, exp_dtype=None,
                   exp_minimum=None, exp_maximum=None,
                   is_primary_key=False, reference=None,
                   required=False):
        super(H5TableColumn, self).__init__(name)

        self.max_value = None
        self.min_value = None
        self.dtype = None
        self.content = None
        self.required = required
        self.primary_key = primary_key

        if exp_minimum:
            if is_number(exp_minimum):
                ref = None
            else:
                ref = reference
            min_rule = CompareRule('min_value', '>=', exp_minimum,
                                   reference=ref,
                                   error_msg='Minimum von '
                                   + exp_minimum + ' unterschritten',
                                   success_msg='Minimum überprüft')
            self.add_rule(min_rule)

        if exp_maximum:
            if is_number(exp_maximum):
                ref = None
            else:
                ref = reference
            max_rule = CompareRule('max_value', '<=', exp_maximum,
                                   reference=ref,
                                   error_msg='Maximum von '
                                   + exp_maximum + ' überschritten',
                                   success_msg='Maximum überprüft')
            self.add_rule(max_rule)

        if exp_dtype:
            type_rule = CompareRule('dtype', '==', exp_dtype,
                                    error_msg='falscher dtype',
                                    success_msg='dtype überprüft')
            self.add_rule(type_rule)

    def update(self, table):
        '''
        look for the column in the given table, the success will be shown
        by the dtype flag
        check for uniqueness of primary keys
        '''
        self.reset()
        if table is None or self.name not in table.dtype.names:
            self.status_flags['dtype'] = NOT_FOUND
            self.max_value = None
            self.min_value = None
            self.dtype = None
            self.content = None
        else:
            self.dtype = table.dtype[self.name]
            if self.required:
                self.status_flags['dtype'] = FOUND
            content = table[self.name]
            if self.dtype.char != 'S':
                self.max_value = content.max()
                self.min_value = content.min()
            #check if all values are unique if primary key
            if self.primary_key and np.unique(content).size != content.size:
                self.status_flags['primary_key'] = (MISMATCH,
                                                    'Werte nicht eindeutig')
            #if content of column is observed, set it
            if 'content' in self._observed:
                self.set('content', list(content))


class H5Array(H5Node):
    '''
    Resource holding information about an array inside a HDF5 resource file

    Parameter
    ---------
    table_path: path of the array inside the h5 file
    '''
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
        return "H5Array {} - {}".format(self.name, self.table_path)

    def update(self, path, h5_in=None):
        '''
        add the minima/maxima
        '''
        table = super(H5Array, self).update(path, h5_in=h5_in)
        if table is not None:
            self.max_value = table.max()
            self.min_value = table.min()
        else:
            self.max_value = None
            self.min_value = None


class Rule(object):
    '''
    monitor a field (by name), not bound to a specific object,
    the given function determines if a given target is reached,
    target values may be referenced to another object (then the fields
    that should be taken from the referenced object have
    to appear as strings in the target_value)

    Parameter
    ---------
    field_name: String,
                the name of the field that will be monitored, contains
                the actual value
    function: monitoring method that will be applied to the monitored field
              has to look like: function(actual_value, target_value)
    target: String or list of Strings,
            the target value(s) that the monitored
            field will be tested to, wildcards ('' and '*') will be ignored
    reference: object, optional
               a referenced object, if set all strings in target with a
               field name will be taken from this referenced object
    '''
    wildcards = ['*', '']

    def __init__(self, field_name, target_value,
                 function, reference=None):
        self.reference = reference
        self.function = function
        self.field_name = field_name
        #cast represented number in target values to float or int
        if isinstance(target_value, str) and is_number(target_value):
            target_value = float(target_value)
            if target_value % 1 == 0:
                target_value = int(target_value)
        self._target = target_value

    @property
    def target(self):
        '''
        return the targeted values

        if referenced: strings in target representing a referenced field name
        will be replaced by the actual values of the field
        '''
        #copy needed (otherwise side effect is caused)
        target = copy.copy(self._target)
        ref_target = []
        former_type = target.__class__
        cast = False
        #look if value is iterable (like lists, arrays, tuples)
        if not hasattr(target, '__iter__'):
            target = [target]
        #iterate over the values
        for i, val in enumerate(target):
            #ignore wildcards
            if val not in self.wildcards:
                #strings may be references to a field
                #(if there is a reference at all)
                if self.reference is not None and isinstance(val, str):
                    #look if the referenced object has a field with this name
                    #and get the referenced value
                    if (self.reference is not None) and \
                       hasattr(self.reference, val):
                        field = getattr(self.reference, val)
                        val = field
                #cast to number if string wraps a number
                if is_number(val):
                    val = float(val)
                    if val % 1 == 0:
                        val = int(val)
            ref_target.append(val)
        #cast back if list is unnecessary
        if len(ref_target) == 1:
            ref_target = ref_target[0]
        return ref_target

    def check(self, obj):
        '''
        check if defined rule is met

        Parameter
        ---------
        obj: object,
             the object holding the monitored field

        Return
        ------
        result: bool,
                True if rule is met, False else
        message: String,
                 details of the check
        '''
        #get the field of the given object
        if not hasattr(obj, self.field_name):
            raise Exception('The object {} does not own a field {}'
                            .format(obj, self.field_name))
        attr_value = getattr(obj, self.field_name)
        #wrap all values with a list (if they are not already)
        target = self.target
        result = self.function(attr_value, target)
        #check if there is a message sent with, if not, append default messages
        if isinstance(result, tuple):
            message = result[1]
            result = result[0]
        elif result:
            message = DEFAULT_MESSAGES[CHECKED_AND_VALID]
        else:
            message = DEFAULT_MESSAGES[MISMATCH]
        #append place where mismatch happened to message
        if not result:
            message += " (in '{}')".format(obj.name)
        return result, message


class DtypeRule(object):
    pass


def is_number(s):
    '''
    check if String represents a number
    '''
    if isinstance(s, list) or isinstance(s, tuple) or s is None:
        return False
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
    '''
    compare the actual value of a monitored field
    with a target value (may be referenced)
    possible operators: '>', '>=', '=>', '<', '=<', '<=', '==', '!='

    Parameter
    ---------
    field_name: String,
                the name of the field that will be checked
    operator: String,
              represents the compare operator
    target: String or list of Strings,
            the target value(s) that the monitored
            field will be tested to, wildcards ('' and '*') will be ignored
    reference: object, optional
               a referenced object, if set all strings in 'value' with a
               field name will be taken from this referenced object
    '''
    mapping = {'>': op.gt,
               '>=': op.ge,
               '=>': op.ge,
               '<': op.lt,
               '=<': op.le,
               '<=': op.le,
               '==': op.eq,
               '!=': op.ne
               }

    def __init__(self, field_name, operator, target, reference=None,
                 error_msg=None, success_msg=None):
        super(CompareRule, self).__init__(field_name, target,
                                          self.compare, reference)
        self.success_msg = success_msg
        self.error_msg = error_msg
        self.operator = operator

    def compare(self, left, right):
        '''
        compare two values (or lists of values)
        '''
        operator = self.mapping[self.operator]
        #make both values iterable
        if not hasattr(left, '__iter__'):
            left = [left]
        if not hasattr(right, '__iter__'):
            right = [right]

        #elementwise compare -> same number of elements needed
        if len(right) != len(left):
            if self.error_msg:
                return False, self.error_msg
            return False
        #compare left and right elementwise
        for i in xrange(len(left)):
            l = left[i]
            r = right[i]
            #ignore wildcards
            if left[i] or right[i] in self.wildcards:
                continue
            #compare the value with the field of the given object
            if not operator(left[i], right[i]):
                #check again if value is number in string
                if isinstance(l, str) and is_number(l):
                    l = float(l)
                if isinstance(r, str) and is_number(r):
                    r = float(r)
                if not operator(l, r):
                    if self.error_msg:
                        return False, self.error_msg
                    return False
        if self.success_msg:
            return True, self.success_msg
        return True
