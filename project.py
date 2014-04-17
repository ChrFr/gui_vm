default_names = {'new_project': 'Neues Projekt',
                 'new_run': 'Neuer Simulationslauf',
                 'result_config': 'Ergebnisse',
                 'input_config': 'Eingaben',
                 'model_config': 'Verkehrsmodel'}

#class NodeData(object):
    #def __init__(self):
        #self._data = {}
    #def add_data(self, name, data):
        #if self._data.has_key(name):
            #raise Exception('{0} already defined'.format(name))
        #else:
            #self._data[name] = data
    #def get_data(self, name):
        #return self._data[name]
    #def set_data(self, name, data):
        #if not self._data.has_key(name):
                    #raise Exception('{0} not defined'.format(name))
        #else:
            #self._data[name] = data


class ProjectTreeNode(object):
    def __init__(self, name, parent=None):
        self.parent = parent
        self.name = name
        self.children = []
        self.rename = True

    def add_child(self, item):
        item.parent = self
        self.children.append(item)

    def remove_child(self, row):
        self.children.pop(row)

    def get_children(self):
        return self.children

    def child_at(self, row):
        return self.children[row]

    def child_count(self):
        return len(self.children)

    def row_of_child(self, child):
        for i, item in enumerate(self.children):
            if item == child:
                return i
        return -1


class Project(ProjectTreeNode):
    def _init__(self, filename=None, parent=None):
        super(Project, self).__init__(default_names['new_project'], parent)
        if filename is not None:
            self.read_config(filename)

    def read_config(self, filename):
        pass

    def write_config(self):
        pass

    def add_run(self):
        new_run = SimRun(default_names['new_run'])
        self.add_child(new_run)

    def remove_run(self, index):
        self.remove_child(index)


class SimRun(ProjectTreeNode):
    def __init__(self, name):
        super(SimRun, self).__init__(name)
        self.add_child(ModelConfig())
        self.add_child(InputConfig())
        self.add_child(ResultsConfig())
        self.rename = False

#### Config Classes ####

class SimRunConfig(ProjectTreeNode):
    def __init__(self, name):
        super(SimRunConfig, self).__init__(name)
        self.name = name
        self.rename = False

class ModelConfig(SimRunConfig):
    def __init__(self):
        super(ModelConfig, self).__init__(default_names['model_config'])
        self.results = None
        self.model_type = 'Wirtschaftsverkehr'


class ResultsConfig(SimRunConfig):
    def __init__(self):
        super(ResultsConfig, self).__init__(default_names['result_config'])
        self.results = None


class InputConfig(SimRunConfig):
    def __init__(self):
        super(InputConfig, self).__init__(default_names['input_config'])
        self.input_file = None



