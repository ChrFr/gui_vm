class TrafficModel(object):
    '''
    base class for traffic models
    '''
    def __init__(self, name):
        self.name = name
        self.subfolder = None
        #dictionary with categories of resources as keys
        #items are lists of the resources to this category
        self.resources = {}

    def process(self):
        pass

    def add_resource(self, resource):
        '''
        add a resource to the traffic model

        Parameters
        ----------
        resource: Resource
        '''
        if not self.resources.has_key(resource.category):
            self.resources[resource.category] = []
        self.resources[resource.category].append(resource)

    def is_complete(self):
        '''
        check if set of resources is complete (all sources are valid)
        '''
        for category in self.resources:
            for resource in self.resources[category]:
                if not resource.is_valid:
                    return False
        return True


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
    def __init__(self, name, subfolder='', category=None,
                 default=None, do_show=True):
        self.name = name
        self.subfolder = subfolder
        self.file_name = default
        #category is the folder as it is displayed later
        if do_show:
            if category is None:
                category = self.subfolder
            self.category = category


    def set_source(self, file_name, file_path = None):
        self.file_name = file_name
        self.file_path = file_path

    @property
    def is_set(self):
        if self.file_name is None:
            return False

    @property
    def is_valid(self):
        return True