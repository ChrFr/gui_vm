#which traffic models are available to choose from
#(same names as classes derived from TrafficModel base class)
TRAFFIC_MODELS = ['Jens', 'Max']
DEFAULT_MODEL = 'Jens'

class TrafficModel(object):
    '''
    base class for traffic models
    '''
    def __init__(self, name):
        self.name = name
        #dictionary with categories of resources as keys
        #items are lists of the resources to this category
        self.resources = {}

    def command(self):
        return ''

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


class Jens(TrafficModel):
    def __init__(self, parent=None):
        super(Jens, self).__init__('Jens')

        activities = Resource('Aktivitaeten', category='Matrizen')
        accessibilities = Resource('Erreichbarkeiten', category='Matrizen')
        net = Resource('Netz1', category='Netze')

        self.add_resource(activities)
        self.add_resource(accessibilities)
        self.add_resource(net)


class Max(TrafficModel):
    def __init__(self, parent=None):
        super(Max, self).__init__('Max')

        something = Resource('irgendwas', category='irgendeine Kategorie')
        bla = Resource('Ressource bla', category='Kategorie blubb')

        self.add_resource(something)
        self.add_resource(bla)


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
    def __init__(self, name, category = 'default',
                 file_path = None, file_name = None):
        self.name = name
        self.category = category
        self.file_name = file_name
        self.file_path = file_path

    def set_source(self, file_name, file_path = None):
        self.file_name = file_name
        self.file_path = file_path

    @property
    def is_valid(self):
        if self.file_name is None:
            return False
        return True