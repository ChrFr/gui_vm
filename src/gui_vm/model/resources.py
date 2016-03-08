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
from collections import OrderedDict
from gui_vm.model.observable import Observable
from gui_vm.model.rules import DtypeCompareRule, CompareRule
import copy

class Status(object):
    #status flags (with ascending priority)
    NOT_CHECKED = 0
    NOT_NEEDED = 1
    FOUND = 2
    CHECKED_AND_VALID = 3
    NOT_FOUND = 4
    MISMATCH = 5
    
    DEFAULT_MESSAGES = ['', 'nicht benötigt', 'vorhanden', 'überprüft',
                        'nicht vorhanden', 'Fehler']
    
    def __init__(self, name):
        self.messages = []
        self.code = self.NOT_CHECKED
        self._flag_dict = {}
        self.name = name
        
    @property
    def flags(self):
        return self._flag_dict.keys()
        
    def add(self, flag):
        if self._flag_dict.has_key(flag):
            print 'Warning: status already contains flag "{}". Addition is ignored.'.format(flag)
            return
        self._flag_dict[flag] = self.NOT_CHECKED, self.DEFAULT_MESSAGES[self.NOT_CHECKED]   
            
    def set(self, flag, value, message=None):
        if isinstance(value, Status):
            self._flag_dict[flag] = value 
            return
        if not message:
            message = self.DEFAULT_MESSAGES[value]
        self._flag_dict[flag] = value, message 
    
    def get(self, flag):
        return self._flag_dict[flag]      
    
    def get_flag_message(self, flag):
        value = self._flag_dict[flag]
        if isinstance(value, Status):
            return ', '.join(value.messages)
        return self._flag_dict[flag][1]         
    
    def get_flag_code(self, flag):
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
                for child_msg in child_msgs:
                    if len(child_msg) > 0 and child_msg not in messages:
                        messages.append(child_msg)              
                if child_status > status_code:
                    status_code = child_status    
                continue
                
            if not isinstance(flag, tuple):
                flag = (flag, self.DEFAULT_MESSAGES[flag])
                
            msg = flag[1]
            if len(msg) > 0 and msg not in messages:
                messages.append(msg)
            if flag[0] > status_code:
                status_code = flag[0]
                
        self.code = status_code
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
        self.required = False
        self.dynamic = False
        #add status flags for the monitored attributes
        self._status = Status(name)
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
        with the actual value, a message and a status flag
        can be nested if there are child resources, their status will
        appear instead of the message

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
        if self._status.code > Status.NOT_NEEDED:
            return True
        else:
            return False

    @property
    def is_valid(self):
        if self._status.code == Status.CHECKED_AND_VALID:
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
        for key, value in self.monitored.items():
            self._status.set(key, Status.NOT_CHECKED)
        for child in self.children:
            child.reset_status()
            self._status.set(child.name, child._status)

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

    #def merge_status(self):
        ##don't show all child messages for resource files (confusing)
        #super(ResourceFile, self).merge_status()
        #status_flag = self.merged_status[0]
        #self.merged_status = status_flag, [Status.DEFAULT_MESSAGES[status_flag]]

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
        if self.filename is None:
            return None, False
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
            self.shape = None
            return None
        self._status.set('table_path', Status.FOUND)
        table = table.read()
        self.shape = table.shape
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
            type_rule = DtypeCompareRule('dtype', '==', exp_dtype,
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
            self._status.set('dtype', Status.NOT_FOUND)
            self.max_value = None
            self.min_value = None
            self.dtype = None
            self.content = None
        else:
            self.dtype = table.dtype[self.name]
            if self.required:
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
            if self.primary_key and np.unique(content).size != content.size:
                
                self._status.set('primary_key', Status.MISMATCH, 'Werte nicht eindeutig')
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
