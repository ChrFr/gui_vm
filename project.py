from copy import deepcopy
from traffic_models import *
import time

default_names = {'new_project': 'Neues Projekt',
                 'ressources': 'Ressourcen',
                 'empty': '<keine Eingabe>',
                 'new_run': 'Neuer Simulationslauf',
                 'result_config': 'Ergebnisse',
                 'input_config': 'Eingaben',
                 'model_config': 'Verkehrsmodel'}

class ProjectTreeNode(object):
    def __init__(self, name, note='', parent=None):
        self.parent = parent
        self.name = name
        self.note = note
        self.children = []
        self.rename = True

    def add_child(self, item):
        item.parent = self
        self.children.append(item)

    def get_child(self, name):
        for child in self.children:
            if child.name == name:
                return child
        raise Exception('no child {0} found in children of {1}'.format(
            name, self.name))

    def has_child(self, name):
        for child in self.children:
            if child.name == name:
                return True
        return False

    def get_row(self, name):
        for i, child in enumerate(self.children):
            if child.name == name:
                return i
        return -1

    def remove_child(self, name):
        row = self.get_row(name)
        self.children.pop(row)

    def remove_child_at(self, row):
        self.children.pop(row)

    def get_children(self):
        return self.children

    def child_at_row(self, row):
        return self.children[row]

    def child_count(self):
        return len(self.children)

    def row_of_child(self, child):
        for i, item in enumerate(self.children):
            if item == child:
                return i
        return -1


class SimRun(ProjectTreeNode):
    def __init__(self, name):
        super(SimRun, self).__init__(name)
        self.model = TrafficModel(default_names['empty'])
        self.note = self.model.name
        self._available = TRAFFIC_MODELS
        self.rename = False

    def set_model(self, name):
        if name in self._available:
            model = globals()[str(name)]()
        for i in reversed(range(self.child_count())):
            self.remove_child_at(i)
        for category in model.ressources:
            category_node = ProjectTreeNode(category)
            self.add_child(category_node)
            for ressource in model.ressources[category]:
                category_node.add_child(RessourceNode(ressource))
        self.note = self.model.name


class Project(ProjectTreeNode):
    def __init__(self, filename=None, parent=None):
        super(Project, self).__init__(default_names['new_project'],
                                      parent=parent)
        if filename is not None:
            self.read_config(filename)
        self.meta = {}
        self.meta['Datum'] = time.strftime("%d.%m.%Y")
        self.meta['Uhrzeit'] = time.strftime("%H:%M:%S")
        self.meta['Autor'] = ''
        self.note = self.meta['Datum']

    def read_config(self, filename):
        pass

    def write_config(self):
        pass

    def add_run(self):
        new_run = SimRun(default_names['new_run'])
        self.add_child(new_run)
        new_run.set_model('Jens')

    def remove_run(self, index):
        self.remove_child(index)

class RessourceNode(ProjectTreeNode):
    '''
    wrap the ressource with a node
    '''
    def __init__(self, ressource,
                parent=None):
        self.ressource = ressource
        note = '<{}>'.format(ressource.source)
        super(RessourceNode, self).__init__(ressource.name, note=note,
                                            parent=parent)


#class AvailableRessources(ProjectTreeNode):
    #def _init__(self, filename=None, parent=None):
        #super(Project, self).__init__(default_names['ressources'], parent)

    #def add_ressource(self, ressource):
        #new_res = deepcopy(ressource)
        #self.add_child(ressource)

##### Config Classes ####

#class SimRunConfig(ProjectTreeNode):
    #def __init__(self, name):
        #super(SimRunConfig, self).__init__(name)
        #self.name = name
        #self.rename = False

#class ModelConfig(SimRunConfig):
    #def __init__(self):
        #super(ModelConfig, self).__init__(default_names['model_config'])
        #self.results = None
        #self.model_type = 'Wirtschaftsverkehr'


#class ResultsConfig(SimRunConfig):
    #def __init__(self):
        #super(ResultsConfig, self).__init__(default_names['result_config'])
        #self.results = None


#class InputConfig(SimRunConfig):
    #def __init__(self):
        #super(InputConfig, self).__init__(default_names['input_config'])
        #self.input_file = None


