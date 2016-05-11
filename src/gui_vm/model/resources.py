# -*- coding: utf-8 -*-

##------------------------------------------------------------------------------
## File:        resources.py
## Purpose:     contains classes wrapping resource files (like h5 etc.)
##
## Author:      Christoph Franke
##
## Created:
## Copyright:   Gertz Gutsche Rümenapp - Stadtentwicklung und Mobilität GbR
##------------------------------------------------------------------------------

from backend import HDF5
import os
import numpy as np
import time
import copy
import re
from collections import OrderedDict
from gui_vm.model.observable import Observable
from gui_vm.model.rules import DtypeCompareRule, CompareRule, Rule

class Status(object):
    '''
    class for managing status flags observing specific attributes (observation is not handled by Status-class)
    and the relations between parent- and child-statuses,
    is organized as a dictionary, values can be Status-objects themselfes
    (parent-child relation is represented this way)
    '''

    #status flags (with ascending priority)
    NOT_CHECKED = 0
    NOT_NEEDED = 1
    FOUND = 2
    CHECKED_AND_VALID = 3
    NOT_FOUND = 4
    MISMATCH = 5

    DEFAULT_MESSAGES = ['', 'nicht explizit benötigt', 'vorhanden', 'überprüft',
                        'nicht vorhanden', 'Fehler']

    def __init__(self):
        self.messages = []
        self.code = self.NOT_CHECKED
        self._flag_dict = {}

    @property
    def flags(self):
        '''
        Return
        ----------------
        list of names of all contained flags
        '''
        return self._flag_dict.keys()

    def add(self, flag):
        '''
        add a new flag, is initialized with 'unchecked'

        Parameter
        ----------------
        flag: name of the flag
        '''
        if self._flag_dict.has_key(flag):
            print 'Warning: status already contains flag "{}". Addition is ignored.'.format(flag)
            return
        self._flag_dict[flag] = self.NOT_CHECKED, self.DEFAULT_MESSAGES[self.NOT_CHECKED]

    def clear(self):
        '''
        remove all status flags
        '''
        self._flag_dict.clear()

    def set(self, flag, value, message=None):
        '''
        set the status-code of a flag, is added if not exisiting,
        else values are overwritten

        Parameter
        ----------------
        flag: name of the flag
        value: status-code (can be status-object as well, becomes child this way)
        message: optional, message belonging to current status of this flag (default message is taken, if not given)
        '''
        if isinstance(value, Status):
            self._flag_dict[flag] = value
            return
        if not message:
            message = self.DEFAULT_MESSAGES[value]
        self._flag_dict[flag] = value, message

    def get(self, flag):
        '''
        get the currently set status of the flag

        Parameter
        ----------------
        flag: name of the flag

        Return
        ----------------
        tuple of (status_code, message)
        '''
        return self._flag_dict[flag]

    def get_flag_message(self, flag):
        '''
        get the currently set status-message of the flag

        Parameter
        ----------------
        flag: name of the flag

        Return
        ----------------
        string
        '''
        value = self._flag_dict[flag]
        if isinstance(value, Status):
            return ', '.join(value.messages)
        return self._flag_dict[flag][1]

    def get_flag_code(self, flag):
        '''
        get the currently set status-code of the flag

        Parameter
        ----------------
        flag: name of the flag

        Return
        ----------------
        int
        '''
        value = self._flag_dict[flag]
        if isinstance(value, Status):
            return value.code
        return self._flag_dict[flag][0]

    def merge(self):
        '''
        calculate and set the status of this resource by checking the
        status of its children, the highest status will be taken
        (ascending hierarchical order of status)
        '''
        status_code = self.NOT_CHECKED
        messages = []
        for flag in self._flag_dict.values():

            # flag is Status itself
            if isinstance(flag, Status):
                flag.merge()
                child_status = flag.code
                child_msgs = flag.messages
                # append error messages only (avoid confusion in GUI)
                if child_status >= self.NOT_FOUND:
                    messages.extend(child_msgs)
                if child_status > status_code:
                    status_code = child_status
                continue

            # no message found -> take default one
            if not isinstance(flag, tuple):
                flag = (flag, self.DEFAULT_MESSAGES[flag])

            if flag[0] > status_code:
                status_code = flag[0]

        self.code = status_code

        # messages should contain at least one message (esp. if no errors occurred)
        if len(messages) == 0:
            messages = [self.DEFAULT_MESSAGES[status_code]]

        self.messages = messages


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
        self.is_required = False
        #add status flags for the monitored attributes
        self._status = Status()
        for key, value in self.monitored.items():
            self._status.add(key)

    def add_child(self, child):
        '''
        add a child resource
        '''
        self.children.append(child)
        self._status.set(child.name, child._status)

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
        self._status.merge()


    @property
    def status(self, overwrite=None):
        '''
        dictionary with pretty attributes as keys and a tuple as values
        with the actual value, a message and a status flag (as int)
        can be nested if there are child resources, their status will
        appear instead of the message
        (does not return the status-object!)

        Return
        ------
        attributes: dict,
                    attribute names as keys, tuple (name of attribute, message
                    or child status, statusflag) as values
        '''

        status_dict = OrderedDict()
        attributes = OrderedDict()

        #add the status of the monitored attributes
        for i, attr in enumerate(self.monitored):
            target = getattr(self, attr)
            pretty_name = self.monitored[attr]
            status_flag = self._status.get(attr)
            if isinstance(status_flag, tuple):
                message = status_flag[1]
                status_flag = status_flag[0]
            else:
                message = Status.DEFAULT_MESSAGES[status_flag]
            attr_tuple = (target, message, status_flag)
            attributes[pretty_name] = attr_tuple
        #add the status of the children
        for child in self.children:
            attributes.update(child.status)
        status_dict[self.name] = (attributes, ', '.join(self._status.messages),
                             self._status.code)
        return status_dict

    @property
    def is_checked(self):
        '''
        returns, if the resource was already checked (doesn't state, if resource is valid or not!)

        Return
        ------
        boolean - true, if resource is already checked, false else
        '''
        if self._status.code > Status.NOT_NEEDED:
            return True
        else:
            return False

    @property
    def is_valid(self):
        '''
        returns, if the resource is valid (= marked as valid after checking without getting errors)

        Return
        ------
        boolean - true, if resource is valid, false else
        '''
        if self._status.code == Status.CHECKED_AND_VALID:
            return True
        else:
            return False

    @property
    def is_found(self):
        '''
        returns, if the resource-file exists

        Return
        ------
        boolean - true, if resource is found, false else
        '''
        if self._status.code == Status.FOUND:
            return True
        else:
            return False

    def validate(self, path):
        '''
        validate the resource and set the status
        '''
        self.update(path)
        #only check rules if resource-file is found
        if self._status.code != Status.NOT_FOUND:
            self._validate(path)
        self._status.merge()

    def _validate(self, path):
        '''
        recursive validation of the children by checking the rules,
        set the status according to the results of the check of the rules
        '''
        for rule in self.rules:
            is_valid, message = rule.check(self)
            if not is_valid:
                self._status.set(rule.field_name, Status.MISMATCH, message)
            else:
                self._status.set(rule.field_name, Status.CHECKED_AND_VALID,
                                                      message)
        for child in self.children:
            child._validate(path)

    def reset_status(self):
        '''
        reset the status flags of the resource and its children recursive
        '''
        self._status.code = Status.NOT_CHECKED
        self._status.clear()
        for key, value in self.monitored.items():
            self._status.set(key, Status.NOT_CHECKED)
        for child in self.children:
            child.reset_status()
            self._status.set(child.name, child._status)

    def remove_children(self):
        '''
        remove all children ('subdivisions' of this resource)
        '''
        if len(self.children) > 0:
            for i in xrange(len(self.children)):
                child = self.children.pop(0)
                child.remove_children()


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
        self.reset_status()
        if self.filename != '' and self.filename is not None:
            filename = os.path.join(path, self.subfolder, self.filename)
            if os.path.exists(filename):
                stats = os.stat(filename)
                t = time.strftime('%d-%m-%Y %H:%M:%S',
                                  time.localtime(stats.st_mtime))
                self.file_modified = t
                self._status.set('filename', Status.FOUND)
                return
        self._status.set('filename', Status.NOT_FOUND)

    @property
    def is_set(self):
        if self.filename is None:
            return False

    def read(self, path):
        '''
        read the resource from file at given path
        When inheriting from Resource, method foo must be overridden.

        Return
        ------------
        tuple (file, boolean) - the opened file and true, if successfully opened
        '''
        raise NotImplementedError
        return None, None

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
        '''
        Override:
        read the resource from H5-file at given path (subfolder and filename of resource will be added automatically)

        Parameters
        ----------
        path: the absolute path to the working directory of the resource (excl. subfolder and filename)

        Return
        ----------
        tuple (file, boolean) - the opened h5-file and true, if successfully opened
        '''
        if self.filename is None:
            return None, False
        h5 = HDF5(os.path.join(path, self.subfolder, self.filename))
        successful = h5.read()
        return h5, successful

    def update(self, path):
        '''
        reads and sets the attributes of all child nodes

        Parameter
        ---------
        path: String, path of the working directory,
                      where the file is in (without subfolder)
        '''
        super(H5Resource, self).update(path)
        h5_in = None
        if path is not None:
            h5_in, success = self.read(path)
        if path is None or not success:
            #set a flag for file not found
            self._status.set('filename', Status.NOT_FOUND, 'keine gueltige HDF5 Datei')
        for child in self.children:
            child.update(path, h5_in=h5_in)
        #close file
        del(h5_in)
        self._status.merge()


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
        if path is None:
            return None
        table = self.read(path, h5_in=h5_in)
        if not table:
            self._status.set('table_path', Status.NOT_FOUND)
            self.set('shape', None)
            return None
        self._status.set('table_path', Status.FOUND)
        table = table.read()
        self.set('shape', table.shape)
        return table

    @property
    def status(self):
        '''
        adds a pretty representation of the dimension to the status gotten from
        the base class
        '''
        status_dict = super(H5Node, self).status
        #pretty print the dimension (instead of tuple (a, b, c) 'a x b x c')
        if self.shape is not None:
            dim = ''
            for v in self.shape:
                dim += '{} x '.format(v)
            dim = dim[:-3]
            dim_status = list(status_dict[self.name][0][self.monitored['shape']])
            dim_status[0] = dim
            status_dict[self.name][0][self.monitored['shape']] = tuple(dim_status)
        return status_dict


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
            if not child.is_required:
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

    def multiply_placeholder(self, placeholder_column, field_name, replacement_list):
        '''
        multiplies the given column, resulting columns differ in the names;
        name of column to multiply should contain the field_name surrounded with
        braces (or what ever is defined as replace_indicators ->e.g. 'xxx{field_name}xxx'),
        will be replaced by the strings in the given list;
        adds the resulting columns as children (number of added columns = length of replacement_list);
        all existing columns matching the pattern of the given column will be removed

        Parameters
        ----------
        placeholder_column: the column to multiply
        field_name: the tag that will be replaced
        replacement_list: list of strings, that the tag will be replaced with
        '''
        pattern = placeholder_column.name

        tmp = []
        tag = Rule.replace_indicators[0] + field_name + Rule.replace_indicators[1]
        regex = placeholder_column.name.replace(tag, '[a-zA-Z\d]+')
        for i in xrange(len(self.children)):
            column = self.children.pop(0)
            if re.search(regex, column.name):
                column.remove_children()
            else:
                tmp.append(column)
        self.children = tmp
        if not replacement_list:
            return
        for replacement in replacement_list:
            new_col_name = pattern.replace(tag, replacement)
            dynamic_column = copy.deepcopy(placeholder_column)
            dynamic_column.name = new_col_name
            dynamic_column.is_required = True
            self.add_child(dynamic_column)

    def from_xml(self, element, reference=None):
        '''
        read and add attributes of the H5 Table from an etree xml element
        including columns and rules

        Parameters
        ----------
        element:    the etree xml element representing a H5Table
        reference:  object, optional
                    a referenced object, created rules are (e.g. min with fieldname)
                    referenced to this object
        '''
        n_rows = element.attrib['n_rows']
        if len(n_rows) > 0:
            dim_rule = CompareRule('shape', '==',
                                   n_rows, reference=reference,
                                   error_msg='falsche Dimension',
                                   success_msg='Dimension überprüft')
            self.add_rule(dim_rule)
        for column_node in element.findall('column'):
            col_name = column_node.attrib['name']
            column = H5TableColumn(col_name, is_required=True)
            column.from_xml(column_node, reference=reference)

            # if name of column shows replacable pattern create placeholder
            do_replace = Rule.replace_indicators[0] in col_name
            if do_replace:
                field_name = col_name[col_name.find(Rule.replace_indicators[0]) +
                                      1:col_name.find(Rule.replace_indicators[1])]
                # on change of the referenced field the dynamic cols will be be
                # cloned from of the placeholder column
                reference.bind(field_name,
                               lambda value: self.multiply_placeholder(column,
                                                                       field_name,
                                                                       value))
            else:
                # only add columns, that don't act as placeholders
                self.add_child(column)

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
    is_required:    bool, optional
                    determines, if the column is required by the traffic model
    '''
    monitored = OrderedDict([('dtype', 'dtype'),
                             ('is_primary_key', 'Primaerschluessel'),
                             ('max_value', 'Maximum'),
                             ('min_value', 'Minimum')])

    def __init__(self, name, exp_dtype=None,
                   exp_minimum=None, exp_maximum=None,
                   is_primary_key=False, reference=None,
                   is_required=False):
        super(H5TableColumn, self).__init__(name)

        self.max_value = None
        self.min_value = None
        self.dtype = None
        self.content = None
        self.is_required = is_required
        self.is_primary_key = is_primary_key

    def update(self, table):
        '''
        look for the column in the given table, the success will be shown
        by the dtype flag
        check for uniqueness of primary keys
        '''

        if table is None or self.name not in table.dtype.names:
            self.reset()
            self._status.set('dtype', Status.NOT_FOUND, 'Spalte fehlt')
            self.max_value = None
            self.min_value = None
            self.dtype = None
            self.content = None
        else:
            self.dtype = table.dtype[self.name]
            if self.is_required:
                self._status.set('dtype', Status.FOUND)
            else:
                self._status.set('dtype', Status.NOT_NEEDED)
            content = table[self.name]
            # für Nicht-String-Variablen checke die Min- und Max-Grenzen
            if self.dtype.char != 'S':
                self.max_value = content.max()
                self.min_value = content.min()
            # für String-Variablen: Konvertiere in UTF 8
            else:
                content = np.char.decode(content, encoding='CP1252')
            #check if all values are unique if primary key
            if self.is_primary_key and np.unique(content).size != content.size:

                self._status.set('is_primary_key', Status.MISMATCH, 'Werte nicht eindeutig')
            #if content of column is observed, set it
            if 'content' in self._observed:
                self.set('content', list(content))


    def from_xml(self, element, reference=None):
        '''
        read and add attributes of the H5 Column from an etree xml element
        including rules

        Parameters
        ----------
        element:    the etree xml element representing the column
        reference:  object, optional
                    a referenced object, created rules are (e.g. min with fieldname)
                    referenced to this object
        '''

        dtype = element.attrib['type']
        minimum = element.attrib['minimum']
        maximum = element.attrib['maximum']
        primary = element.attrib['is_primary_key']

        if primary == '1' or primary == 'True':
            self.is_primary_key = True
        else:
            self.is_primary_key = False

        if minimum:
            if is_number(minimum):
                ref = None
            else:
                ref = reference
            min_rule = CompareRule('min_value', '>=', minimum,
                                   reference=ref,
                                   error_msg='Minimum von '
                                   + minimum + ' unterschritten',
                                   success_msg='Minimum überprüft')
            self.add_rule(min_rule)

        if maximum:
            if is_number(maximum):
                ref = None
            else:
                ref = reference
            max_rule = CompareRule('max_value', '<=', maximum,
                                   reference=ref,
                                   error_msg='Maximum von '
                                   + maximum + ' überschritten',
                                   success_msg='Maximum überprüft')
            self.add_rule(max_rule)

        if dtype:
            type_rule = DtypeCompareRule('dtype', '==', dtype,
                                         error_msg='falscher dtype',
                                         success_msg='dtype überprüft')
            self.add_rule(type_rule)


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

    def from_xml(self, element, reference=None):

        minimum = element.attrib['minimum']
        maximum = element.attrib['maximum']
        dimension = tuple(element.attrib['dimension'].split(' x '))
        if minimum != '':
            if is_number(minimum):
                ref_min = None
            else:
                ref_min = reference
            min_rule = CompareRule('min_value', '>=', minimum,
                                   reference=ref_min,
                                   error_msg='Minimum unterschritten',
                                   success_msg='Minimum überprüft')
            self.add_rule(min_rule)
        if maximum != '':
            if is_number(maximum):
                ref_max = None
            else:
                ref_max = reference
            max_rule = CompareRule('max_value', '<=', maximum,
                                   reference=ref_max,
                                   error_msg='Maximum überschritten',
                                   success_msg='Maximum überprüft')
            self.add_rule(max_rule)
        if (np.array(dimension) != '').any():
            if len(dimension) == 1:
                dimension = dimension[0]
            dim_rule = CompareRule('shape', '==', dimension,
                                   reference=reference,
                                   error_msg='falsche Dimension',
                                   success_msg='Dimension überprüft')
            self.add_rule(dim_rule)

def is_number(s):
    '''
    check if String represents a number
    '''
    try:
        float(s)
        return True
    except ValueError:
        return False
