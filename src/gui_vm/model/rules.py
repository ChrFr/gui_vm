# -*- coding: utf-8 -*-

##------------------------------------------------------------------------------
## File:        rules.py
## Purpose:     different rules for monitoring and validating attributes
##
## Author:      Christoph Franke
##
## Created:
## Copyright:   Gertz Gutsche Rümenapp - Stadtentwicklung und Mobilität GbR
##------------------------------------------------------------------------------

import operator as op
import copy

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
    # strings indicating beginning/end of a field-name, that shall be the basis of the rule instead of a number
    replace_indicators = ['{', '}']
    # wildcards will be ignored while checking the rule
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
    def target_value(self):
        '''
        return the targeted values

        if referenced: strings in target representing a referenced field name
        will be replaced by the actual values of the field
        '''
        # copy needed (otherwise side effect is caused)
        target = copy.copy(self._target)
        ref_target = []
        former_type = target.__class__
        cast = False
        # look if value is iterable (like lists, arrays, tuples)
        if not hasattr(target, '__iter__'):
            target = [target]
        # iterate over the values
        for i, val in enumerate(target):
            #ignore wildcards
            if val not in self.wildcards:
                # strings may be references to a field
                # (if there is a reference at all)
                if self.reference is not None and not is_number(val):
                    # find fieldname in between indicating brackets
                    val = val[val.find(self.replace_indicators[0]) +
                              1:val.find(self.replace_indicators[1])]

                    # look if the referenced object has a field with this name
                    # and get the referenced value
                    if hasattr(self.reference, val):
                        field = getattr(self.reference, val)
                        val = field
                # cast to number if string wraps a number
                if is_number(val):
                    val = float(val)
                    if val % 1 == 0:
                        val = int(val)
            ref_target.append(val)
        # cast back if list is unnecessary
        if len(ref_target) == 1:
            ref_target = ref_target[0]
        return ref_target

    @property
    def target_pretty_names(self):
        if not self.reference or not hasattr(self.reference, 'monitored'):
            return None
        target = copy.copy(self._target)
        if not hasattr(target, '__iter__'):
            target = [target]
        pretty_names = []
        for val in target:
            val = val[val.find(self.replace_indicators[0]) +
                      1:val.find(self.replace_indicators[1])]
            name = self.reference.monitored[val]
            pretty_names.append(name)
        return pretty_names

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
        target_value = self.target_value
        result = self.function(attr_value, target_value)
        #check if there is a message sent with, if not, append default messages
        if isinstance(result, tuple):
            message = result[1]
            result = result[0]
        elif result:
            message = DEFAULT_MESSAGES[CHECKED_AND_VALID]
        else:
            message = DEFAULT_MESSAGES[MISMATCH]

        if not result:
            pretty_names = self.target_pretty_names
            if pretty_names:
                message += ' (Referenz auf {})'.format(self.target_pretty_names)
        return result, message


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
        compare two values (or lists of values elementwise)
        '''
        operator = self.mapping[self.operator]
        #make both values iterable
        if not hasattr(left, '__iter__'):
            left = [left]
        if not hasattr(right, '__iter__'):
            right = [right]

        if self.error_msg:
            error_msg = self.error_msg + ' - erwartet: {} {}'.format(self.operator, right)

        #elementwise compare -> same number of elements needed
        if len(right) != len(left):
            return False, error_msg
        #compare left and right elementwise
        for i in xrange(len(left)):
            l = left[i]
            r = right[i]
            #ignore wildcards
            if (left[i] in self.wildcards) or (right[i] in self.wildcards):
                continue
            #compare the value with the field of the given object
            if not operator(left[i], right[i]):
                #check again if value is number in string
                if isinstance(l, str) and is_number(l):
                    l = float(l)
                if isinstance(r, str) and is_number(r):
                    r = float(r)
                if not operator(l, r):
                    return False, error_msg
        if self.success_msg:
            return True, self.success_msg
        return True

class DtypeCompareRule(CompareRule):
    wildcards = []

