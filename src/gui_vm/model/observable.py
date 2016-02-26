# -*- coding: utf-8 -*-

##------------------------------------------------------------------------------
## File:        observable.py
## Purpose:     class with observable attributes
##
## Author:      Christoph Franke
##
## Created:     
## Copyright:   Gertz Gutsche Rümenapp - Stadtentwicklung und Mobilität GbR
##------------------------------------------------------------------------------

class Observable(object):
    def __init__(self):
        # stores observed attributes and callbacks
        self._observed = {}
        # stores connected callbacks that shall be called on emit
        self.connected = []

    def get(self, attribute):
        '''
        get the attribute
        '''
        return getattr(self, attribute)

    def set(self, attribute, value):
        '''
        set the attribute with the given value
        '''
        setattr(self, attribute, value)
        if attribute in self._observed:
            callbacks = self._observed[attribute]
            for callback in callbacks:
                callback(value)
        self.emit()

    def reset(self):
        for attribute in self._observed:
            self.set(attribute, None)
        self.emit()
            
    def on_change(self, callback):        
        self.connected.append(callback)
    
    def emit(self):
        for callback in self.connected:
            callback()

    def bind(self, attribute, callback):
        '''
        bind an observer to the given attribute, callback function is called
        with the value, if attribute changes
        '''
        if self._observed.has_key(attribute):
            # prevent that same callback is added twice
            if callback not in self._observed[attribute]:
                self._observed[attribute].append(callback)
        else:
            self._observed[attribute] = [callback]

    def unbind(self, attribute, callback):
        pass