class Observable(object):
    def __init__(self):
        self._observed = {}

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

    def reset(self):
        for attribute in self._observed:
            self.set(attribute, None)

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