from copy import deepcopy
from traffic_models import *
import os
import time

default_names = {'new_project': 'Neues Projekt',
                 'resources': 'Resourcen',
                 'empty': '<keine Eingabe>',
                 'new_run': 'Neuer Simulationslauf',
                 'result_config': 'Ergebnisse',
                 'input_config': 'Eingaben',
                 'model_config': 'Verkehrsmodel'}

class ProjectTreeNode(object):
    '''
    Base class of nodes in the project tree
    '''
    def __init__(self, name, parent=None):
        self.parent = parent
        self.name = name
        self.children = []
        self.rename = True

    @property
    def note(self):
        '''
        short textual info to display in ui tree,
        should be overwritten by derived classes

        Return
        ------
        String
        '''
        return ''

    def add_child(self, child):
        '''
        add a node as a child

        Parameters
        ----------
        child: ProjectTreeNode,
               node, that will be new child of this node
        '''
        child.parent = self
        self.children.append(child)

    def get_child(self, name):
        '''
        get a direct child by name (first one found)

        Parameters
        ----------
        name: String,
              name of the child node

        Return
        ------
        child: ProjectTreeNode
        '''
        for child in self.children:
            if child.name == name:
                return child
        return None

    def has_child(self, name):
        '''
        look if node has a child with given name

        Parameters
        ----------
        name: String,
              name of the child node

        Return
        ------
        Boolean, True if node has a child with this name, else False
        '''
        for child in self.children:
            if child.name == name:
                return True
        return False

    def get_row(self, name):
        '''
        get the row of the child with the given name (first one found)

        Parameters
        ----------
        name: String,
              name of the child node

        Return
        ------
        row: int, number in list of children
        '''
        for i, child in enumerate(self.children):
            if child.name == name:
                return i
        return -1

    def remove_child(self, name):
        '''
        remove a child with the given name (first one found)

        Parameters
        ----------
        name: String,
              name of the child node
        '''
        row = self.get_row(name)
        self.children.pop(row)

    def remove_child_at(self, row):
        '''
        remove a child with in the given row

        Parameters
        ----------
        row: int,
             place in list of children
        '''
        self.children.pop(row)

    def get_children(self):
        '''
        get all children of node

        Parameters
        ----------
        Array of ProjectTreeNodes
        '''
        return self.children

    def child_at_row(self, row):
        '''
        get a child at given row

        Parameters
        ----------
        row: int,
             place in list of children

        Return
        ------
        child: ProjectTreeNode
        '''
        return self.children[row]

    def child_count(self):
        '''
        get number of children

        Return
        ------
        int, number of children
        '''
        return len(self.children)

    def row_of_child(self, child):
        '''
        get the row of the given child

        Parameters
        ----------
        child: ProjectTreeNode,
               child node to look for

        Return
        ------
        row: int, number in list of children
        '''
        for i, item in enumerate(self.children):
            if item == child:
                return i
        return -1


class SimRun(ProjectTreeNode):
    '''
    Node that holds informations about the a simulation run (e.g. the
    used traffic model)
    the resources are its children
    '''
    def __init__(self, name=None):
        super(SimRun, self).__init__(name)
        self.model = TrafficModel(default_names['empty'])
        self._available = TRAFFIC_MODELS
        self.rename = False

    @property
    def note(self):
        '''
        short textual info to display in ui tree

        Return
        ------
        String
        '''
        note = self.model.name
        return note

    def set_model(self, name):
        '''
        set the traffic model of the sim run
        '''
        if name in self._available:
            self.model = globals()[str(name)]()
            #remove the old children of the sim run (including resources)
            for i in reversed(range(self.child_count())):
                self.remove_child_at(i)
            #add the resources needed by the traffic model, categorized
            for category in self.model.resources:
                category_node = ProjectTreeNode(category)
                self.add_child(category_node)
                for resource in self.model.resources[category]:
                    category_node.add_child(ResourceNode(resource))
        else:
            raise Exception('Traffic Model {0} not available'.format(name))


class Project(ProjectTreeNode):
    '''
    Node that holds the informations about the project
    the simulation runs and their resources are its children
    '''
    def __init__(self, filename=None, parent=None):
        super(Project, self).__init__(default_names['new_project'],
                                      parent=parent)
        if filename is not None:
            self.read_config(filename)
        self.meta = {}
        self.meta['Datum'] = time.strftime("%d.%m.%Y")
        self.meta['Uhrzeit'] = time.strftime("%H:%M:%S")
        self.meta['Autor'] = ''

    @property
    def note(self):
        '''
        short textual info to display in ui tree

        Return
        ------
        String
        '''
        note = self.meta['Datum']
        return note


    def read_config(self, filename):
        pass

    def write_config(self):
        pass

    def add_run(self, name=None):
        if name is None:
            name = 'Simulationslauf {}'.format(self.child_count())
        new_run = SimRun(name)
        self.add_child(new_run)
        new_run.set_model(DEFAULT_MODEL)

    def remove_run(self, index):
        self.remove_child(index)

class ResourceNode(ProjectTreeNode):
    '''
    wrap a resource in a node

    Parameters
    ----------
    resource: Resource,
              resource of the traffic model
    '''
    def __init__(self, resource,
                parent=None):
        self.resource = resource
        super(ResourceNode, self).__init__(resource.name,
                                           parent=parent)

    @property
    def note(self):
        '''
        short textual info to display in ui tree

        Return
        ------
        String
        '''
        if self.resource.file_name is None:
            source = 'nicht angegeben'
        else:
            source = self.resource.file_name
        note = '<{}>'.format(source)
        return note

    @property
    def source(self):
        '''
        Return
        ------
        full path of the resource file
        '''
        if self.resource.file_path is None:
            file_path = os.getcwd()
        if self.resource.file_name is None:
            source = 'nicht angegeben'
        else:
            source = os.path.join(file_path, file_name)
        return source
