#which traffic models are available to choose from
#(same names as classes derived from TrafficModel base class)
TRAFFIC_MODELS = ['Jens', 'Max']

class TrafficModel(object):
    '''
    base class for traffic models
    '''
    def __init__(self, name):
        self.name = name
        self.ressources = {}

    def command(self):
        return ''

    def add_ressource(self, ressource):
        if not self.ressources.has_key(ressource.category):
            self.ressources[ressource.category] = []
        self.ressources[ressource.category].append(ressource)

    def is_complete(self):
        '''
        check if set of ressources is complete (all sources are set)
        '''
        for category in self.ressources:
            for ressource in self.ressources[category]:
                if not ressource.is_set:
                    return False
        return True

    def is_set(self):
        if len(self.ressources):
            return False


class Jens(TrafficModel):
    def __init__(self, parent=None):
        super(Jens, self).__init__('Jens')

        activities = Ressource('Aktivitaeten', category='Matrizen')
        accessibilities = Ressource('Erreichbarkeiten', category='Matrizen')
        net = Ressource('Netz1', category='Netze')

        self.add_ressource(activities)
        self.add_ressource(accessibilities)
        self.add_ressource(net)


class Max(TrafficModel):
    def __init__(self, parent=None):
        super(Max, self).__init__('Max')

        something = Ressource('irgendwas', category='Matrizen')
        bla = Ressource('bla', category='Netze')

        self.add_ressource(something)
        self.add_ressource(bla)


class Ressource(object):
    def __init__(self, name, category = 'default', source = None):
        self.name = name
        self.category = category
        if not source:
            self.is_set = False
            self.source = ''
        else:
            self.source = source

    def set_source(self, path):
        self.is_set = True
        self.source = path

    def is_valid(self):
        return False