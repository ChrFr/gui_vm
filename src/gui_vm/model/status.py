# -*- coding: utf-8 -*-

##------------------------------------------------------------------------------
## File:        status.py
## Purpose:     status informations for resources
##
## Author:      Christoph Franke
##
## Created:     26.02.2016
## Copyright:   Gertz Gutsche Rümenapp - Stadtentwicklung und Mobilität GbR
##------------------------------------------------------------------------------

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

    def __init__(self, name, attributes=None):
        self.overall_status = NOT_CHECKED, []
        if attributes:
            self.add_attributes(attributes)
            self.messages = []

    def add_attribute(self, attribute):    
        self.status_flags[attribute] = (NOT_CHECKED,
                                        DEFAULT_MESSAGES[NOT_CHECKED])    

    def add_attributes(self, attributes):    
        for attribute in attributes:
            self.add_attribute(attribute)