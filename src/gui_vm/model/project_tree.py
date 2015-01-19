from copy import deepcopy
import os
import time
import imp
from lxml import etree
from shutil import copytree
from gui_vm.config.config import Config
from gui_vm.model.resources import ResourceFile
from gui_vm.model.traffic_model import TrafficModel
from gui_vm.model.observable import Observable
from gui_vm.model.backend import hard_copy

#dictionary defines how classes are called when written to xml
#also used while reading xml project config
XML_CLASS_NAMES = {
    'Scenario': 'Szenario',
    'Project': 'Projekt',
    'InputNode': 'Eingabe',
    'TreeNode': 'Layer',
    'OutputNode': 'Ergebnis'
}

config = Config()
config.read()


class TreeNode(Observable):
    '''
    Base class of nodes in the project tree
    '''
    def __init__(self, name, parent=None):
        super(TreeNode, self).__init__()
        self.parent = parent
        self.name = name
        self.children = []
        self.is_checked = False
        self.is_valid = True
        self._locked = False

    def remove(self):
        self.parent.remove_child(self.name)
        self.parent = None
        self.remove_all_children()

    def add_to_xml(self, parent):
        '''
        converts all needed information of this node and recursive of
        its children to xml and attaches it to the given xml parent

        Parameters
        ----------
        parent: SubElement,
                this node will be added to it
        '''
        xml_element = etree.SubElement(
            parent, XML_CLASS_NAMES[self.__class__.__name__])
        xml_element.attrib['name'] = self.name
        for child in self.children:
            child.add_to_xml(xml_element)
        return xml_element

    def from_xml(self, element):
        '''
        read the basic attributes from element and assign them to the node
        '''
        if element.attrib.has_key('name'):
            self.name = element.attrib['name']

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

    @property
    def locked(self):
        '''
        Return
        ------
        locked True, if node or any parent of node is locked
               False, if not locked (and parents not locked)
        '''
        if self._locked:
            return True
        if self.parent:
            return self.parent.locked
        else:
            return False

    @locked.setter
    def locked(self, enabled):
        '''
        Setter for locked status of node
        '''
        self._locked = enabled

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

    def find_all(self, name):
        '''
        find all children by name (deep traversal)

        Parameters
        ----------
        name: String,
              name of the child node

        Return
        ------
        children: list of ProjectTreeNodes
        '''
        children = []
        if self.name == name:
            children.extend([self])
        for child in self.children:
            children.extend(child.find_all(name))
        return children

    def find_all_by_class(self, node_class):
        '''
        find all children by name (deep traversal)

        Parameters
        ----------
        classname: String,
                   name of the class of the nodes to look for

        Return
        ------
        children: list of ProjectTreeNodes
        '''
        children = []
        #print '{}: {}'.format(self.name, self.__class__.__name__)
        if isinstance(self, node_class):
            children.extend([self])
        for child in self.children:
            children.extend(child.find_all_by_class(node_class))
        return children

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
        if row > -1:
            child = self.children.pop(row)
            child.remove()

    def remove_child_at(self, row):
        '''
        remove a child with in the given row

        Parameters
        ----------
        row: int,
             place in list of children
        '''
        child = self.children.pop(row)
        child.remove()

    def remove_all_children(self):
        if len(self.children) > 0:
            for i in xrange(len(self.children)):
                self.children.pop(0).remove()

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
        if len(self.children) <= row:
            return None
        return self.children[row]

    @property
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

    def get_parent_by_class(self, node_class):
        '''
        get the next parent with the given object's class
        return None, if not found

        Parameters
        ----------
        name: String, name of the class

        Return
        ------
        node: ProjectTreeNode, the parent node with this class
        '''
        node = self
        while node.parent is not None:
            node = node.parent
            if isinstance(node, node_class):
                return node
        return None

    def replace_child(self, child, node):
        '''
        replace a child with another one

        Parameters
        ----------
        child: ProjectTreeNode,
               the child to be removed
        node:  ProjectTreeNode,
               the node to be inserted at place the child was before
        '''
        row = self.row_of_child(child)
        self.children.pop(row).remove()
        self.children.insert(row, node)
        node.parent = self

    def update(self):
        '''
        update the the node and its children, if sth shall happen, it has to
        be defined in the subclasses
        '''
        for child in self.children:
            child.update()

    @property
    def children_names(self):
        names = []
        for child in self.children:
            names.append(child.name)
        return names

    def clone(self, name=None):
        clone = deepcopy(self)
        clone.parent = None
        if name:
            clone.name = name
        return clone


class Scenario(TreeNode):
    '''
    Node that holds informations about the a simulation run (e.g. the
    used traffic model)
    the resources are its children
    '''
    INPUT_NODES = 'Eingaben'
    OUTPUT_NODES = 'Ausgaben'

    def __init__(self, model=None, name=None, parent=None):
        super(Scenario, self).__init__(name, parent=parent)
        #create a subnode to put all resources in
        if model is not None:
            self.set_model(model)
        self.locked = False

    @property
    def meta(self):
        return self.model.characteristics

    @property
    def default_folder(self):
        name = self.model.name
        return config.settings['trafficmodels'][name]['default_folder']

    @property
    def path(self):
        if self.get_parent_by_class(Project).project_folder is None:
            return None
        return os.path.join(
            self.get_parent_by_class(Project).project_folder,
            self.name)

    @property
    def output_path(self):
        return os.path.join(
            self.path, self.OUTPUT_NODES)

    @property
    def complete_demand_file(self):
        full_out_path = os.path.join(self.output_path, 'Gesamtlauf')
        demand_file = os.path.join(full_out_path, self.name + '.h5')
        return demand_file

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

    def run(self, process, run_name, callback=None):
        full_out_path = os.path.join(self.output_path, run_name)
        demand_file = os.path.join(self.name + '.h5')
        #full_out_path = os.path.split(self.complete_demand_file)[0]
        #self.model.run(self.name,
                       #process,
                       #self.get_inputs(),
                       #output_path=full_out_path,
                       #callback=callback)
        result = self.add_results(run_name, demand_file)
        #hard_copy(results_file, result.full_path)
        #self.get_parent_by_class(Project).emit()

    def add_results(self, run_name, filename):
        results_node = self.get_child(self.OUTPUT_NODES)
        if not results_node:
            results_node = TreeNode(self.OUTPUT_NODES)
            self.add_child(results_node)
        results_run = results_node.get_child(run_name)
        if not results_run:
            results_run = OutputNode(name=run_name, parent=results_node)
            results_node.add_child(results_run)
        results_run.set_source(os.path.join(run_name, filename))
        return results_run

    def validate(self):
        resource_nodes = self.get_inputs()
        self.is_valid = True
        for node in resource_nodes:
            node.validate()
            if node.is_checked and not node.is_valid:
                #node.parent.checked = True
                #node.parent.is_valid = False
                self.is_valid = False
        self.is_checked = True

    def get_default_scenario(self):
        '''
        get the defaults from the default xml depending on the model
        '''
        default_project_file = os.path.join(self.default_folder,
                                            TrafficModel.FILENAME_DEFAULT)
        #get the default simrun(scenario) for the traffic model
        #from the default file
        tmp_root = TreeNode('default_root')
        try:
            defaults = XMLParser.read_xml(tmp_root, default_project_file)
        except:
            return None
        default_model = defaults.find_all(self.model.name)[0]
        return default_model

    def reset_to_default(self):
        '''
        reset the simrun to the defaults
        '''
        default_model = self.get_default_scenario()
        if not default_model:
            return None
        #set the original sources to the files in the default folder
        for res_node in default_model.get_inputs():
            res_node.original_source = os.path.join(self.default_folder,
                                                    default_model.name,
                                                    self.INPUT_NODES,
                                                    res_node.source)
        #swap this node with the default one
        parent = self.parent
        parent.replace_child(self, default_model)
        default_model.name = self.name
        default_model.locked = False
        return default_model

    def get_input(self, name):
        '''
        get a resource node by name

        Parameters
        ----------
        name: String, name of the resource
        '''
        found = self.find_all(name)
        res_nodes = []
        for node in found:
            if isinstance(node, ResourceNode):
                res_nodes.append(node)
        if len(res_nodes) > 2:
            raise Exception('Multiple Definition of resource {}'
                            .format(self.name))
        return res_nodes[0]

    def get_inputs(self):
        return self.find_all_by_class(InputNode)

    def set_model(self, name):
        '''
        set the traffic model of the sim run, create new traffic model and
        integrate it into the project tree

        Parameters
        ----------
        name: String, name of the traffic model
        '''
        #append resources of model to resource subnode
        input_nodes = self.get_child(self.INPUT_NODES)
        if not input_nodes:
            input_nodes = TreeNode(self.INPUT_NODES)
            self.add_child(input_nodes)
        model = TrafficModel.new_specific_model(name)
        if model:
            self.model = model
            self.model.update(self.path)
            #remove the old children of the sim run (including resources)
            input_nodes.remove_all_children()

            #categorize resources
            res_dict = {}
            resources = self.model.resources.values()
            for resource in resources:
                if not res_dict.has_key(resource.subfolder):
                    res_dict[resource.subfolder] = []
                res_dict[resource.subfolder].append(resource)
            #add the resources needed by the traffic model, categorized
            for subfolder in res_dict:
                layer_node = TreeNode(subfolder)
                input_nodes.add_child(layer_node)
                for resource in res_dict[subfolder]:
                    layer_node.add_child(InputNode(resource.name,
                                                   parent=layer_node))
        else:
            raise Exception('Traffic Model {0} not available'.format(name))

    def add_to_xml(self, parent):
        '''
        converts all needed information of this node and recursive of
        its children to xml and attaches it to the given parent

        Parameters
        ----------
        parent: SubElement,
                this node will be added to it
        '''
        xml_element = super(Scenario, self).add_to_xml(parent)
        xml_element.attrib['locked'] = 'true' if self.locked else 'false'
        tm = etree.Element('Verkehrsmodell')
        tm.text = self.model.name
        xml_element.insert(0, tm)

    def from_xml(self, element):
        '''
        read the basic attributes from element and assign them to the node

        Parameters
        ----------
        element: SubElement,
                 xml node containing informations about this project node
        '''
        super(Scenario, self).from_xml(element)
        #init the traffic model before resources can be set
        tm_name = element.find('Verkehrsmodell').text
        model = TrafficModel.new_specific_model(tm_name)
        if model:
            self.model = model
            self.model.update(self.path)
        else:
            raise Exception('Traffic Model {0} not available'.format(tm_name))
        #lock scenario, if defined in xml
        #_locked has to be set (instead of locked)
        if 'locked' in element.attrib and element.attrib['locked'] == 'true':
            self._locked = True
        else:
            self._locked = False


class Project(TreeNode):
    '''
    Node that holds the informations about the project
    the simulation runs and their resources are its children
    '''
    FILENAME_DEFAULT = 'project.xml'

    def __init__(self, name, project_folder=None, parent=None):
        super(Project, self).__init__(name, parent=parent)
        self.project_folder = project_folder  #os.getcwd()
        #all projects are stored in xmls with the same name
        self.meta = {}
        self.meta['Datum'] = time.strftime("%d.%m.%Y")
        self.meta['Uhrzeit'] = time.strftime("%H:%M:%S")
        self.meta['Autor'] = ''

    def set_meta(self, key, value):
        self.meta[key] = value

    @property
    def filename(self):
        return os.path.join(self.project_folder, self.FILENAME_DEFAULT)

    def add_to_xml(self, parent):
        '''
        converts all needed information of this node and recursive of
        its children to xml and attaches it to the given parent

        Parameters
        ----------
        parent: SubElement,
                this node will be added to it
        '''
        xml_element = super(Project, self).add_to_xml(parent)
        meta = etree.Element('Meta')
        for meta_data in self.meta:
            etree.SubElement(meta, meta_data).text = self.meta[meta_data]
        xml_element.insert(0, meta)

    def from_xml(self, element):
        '''
        read the basic attributes from element and assign them to the node

        Parameters
        ----------
        element: SubElement,
                 xml node containing informations about this project node
        '''
        super(Project, self).from_xml(element)
        for subelement in element:
            if subelement.tag == 'Meta':
                for submeta in subelement:
                    self.meta[submeta.tag] = submeta.text

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

    def add_scenario(self, model, name=None):
        if name is None:
            name = 'Szenario {}'.format(self.child_count)
        #copytree(os.path.join(DEFAULT_FOLDER, 'Maxem'),
                 #os.path.join(self.project_folder, name))
        new_run = Scenario(model, name, parent=self)
        self.add_child(new_run)


class ResourceNode(TreeNode):
    '''
    wrap a resource in a node, link to the resource held by the
    traffic model

    Parameters
    ----------
    resource: Resource,
              resource of the traffic model
    '''
    def __init__(self, name,
                 parent=None):
        self.resource_name = name
        super(ResourceNode, self).__init__(name, parent=parent)
        self.original_source = self.full_source
        self.subfolder = ''

    @property
    def status(self):
        return self.resource.status

    def add_to_xml(self, parent):
        '''
        converts all needed information of this node and recursive of
        its children to xml and attaches it to the given parent

        Parameters
        ----------
        parent: SubElement,
                this node will be added to it
        '''
        xml_element = super(ResourceNode, self).add_to_xml(parent)
        etree.SubElement(
            xml_element, 'Quelle').text = self.original_source
        source = self.source
        etree.SubElement(
            xml_element, 'Projektdatei').text = self.source

    def from_xml(self, element):
        '''
        read the basic attributes from element and assign them to the node

        Parameters
        ----------
        element: SubElement,
                 xml node containing informations about this project node
        '''
        super(ResourceNode, self).from_xml(element)
        if self.model is None:
            raise Exception('The traffic model of the simrun has to be'+
                            'defined before defining its resources!')
        self.resource_name = self.name
        self.original_source = element.find('Quelle').text
        source = element.find('Projektdatei').text
        self.source = source

    @property
    def model(self):
        return self.get_parent_by_class(Scenario).model

    @property
    def scenario_path(self):
        return self.get_parent_by_class(Scenario).path

    @property
    def note(self):
        '''
        short textual info to display in ui tree

        Return
        ------
        String
        '''
        filename = self.resource.filename
        if filename is None or filename == '':
            filename = 'nicht gesetzt'
        note = '<{}>'.format(filename)
        return note

    @property
    def source(self):
        '''
        Return
        ------
        path of the resource file within the ressources folder
        '''
        if (not hasattr(self, 'resource') or
            self.resource is None or
            self.resource.filename is None or
            self.resource.filename == ''):
            return None
        source = os.path.join(self.resource.subfolder,
                              self.resource.filename)
        return source

    @property
    def full_path(self):
        return os.path.join(self.resources_path, self.resource.subfolder)

    @source.setter
    def source(self, subpath):
        if subpath is not None:
            subfolder, filename = os.path.split(subpath.replace('\\','/'))
        else:
            filename = None
            subfolder = None
        #only set filename, because subfolder will be determined
        #by the category
        self.resource.subfolder = subfolder
        self.resource.set_source(filename)

    @property
    def full_source(self):
        '''
        Return
        ------
        full path of the resource file
        '''
        #join path with simrun path to get full source
        source = self.source
        if self.resources_path is None:
            return None
        if self.source is not None:
            source = os.path.join(
                self.resources_path, self.source)
        return source

    @property
    def resources_path(self):
        '''
        path to the resources folder
        '''
        scen_path = self.scenario_path
        if not scen_path:
            return None
        return os.path.join(scen_path, self.subfolder)

    def set_source(self, filename):
        '''
        set the path and filename of the resource

        Parameters
        ----------
        filename: String, path + name of file
        '''
        self.original_source = filename
        self.source = filename

    def update(self):
        self.resource.update(self.resources_path)

    def validate(self):
        self.resource.validate(self.resources_path)
        self.is_checked = self.resource.is_checked
        self.is_valid = self.resource.is_valid

    def reset_to_default(self):
        '''
        reset the simrun to the defaults
        no real reset, only setting of source, because the resource can't be
        set to the old model (incl. references of rules and resource list
        of model) at the moment
        '''
        scenario = self.get_parent_by_class(Scenario)
        default_model = scenario.get_default_scenario()
        #find corresponding default resource node
        res_default = default_model.get_input(self.name)
        #rename source
        self.resource.filename = res_default.resource.filename
        self.resource.subfolder = res_default.resource.subfolder
        self.original_source = os.path.join(scenario.default_folder,
                                            default_model.name,
                                            Scenario.INPUT_NODES,
                                            self.source)


class InputNode(ResourceNode):
    '''
    wrap a resource in a node, link to the resource held by the
    traffic model

    Parameters
    ----------
    resource: Resource,
              resource of the traffic model
    '''
    def __init__(self, name,
                 parent=None):
        super(InputNode, self).__init__(name, parent=parent)
        self.subfolder = Scenario.INPUT_NODES

    @property
    def resource(self):
        '''
        the resources are held by the traffic model, this node only
        holds a kind of reference to it (via the dict)
        '''
        if self.resource_name in self.model.resources.keys():
            return self.model.resources[self.resource_name]
        else:
            return None


class OutputNode(ResourceNode):
    def __init__(self, name=None, filename=None, parent=None, subfolder=None):
        super(OutputNode, self).__init__(name, parent=parent)
        self.subfolder = Scenario.OUTPUT_NODES
        self.resource = ResourceFile(name, filename=filename, 
                                     subfolder=name)
        
    @property
    def scenario_path(self):
        return self.get_parent_by_class(Scenario).path
    
    @property
    def status(self):
        return None    

class XMLParser(object):
    '''
    class that holds functions to read and write xml
    '''
    inversed_names = {v: k for k, v in XML_CLASS_NAMES.items()}

    def __init__(self):
        pass

    @classmethod
    def read_xml(self, root, filename):
        tree = etree.parse(filename)
        root_element = tree.getroot()
        if root_element.tag == 'GUI_VM_PROJECT':
            self.build_xml(root_element, root)
        else:
            print "Warning: node GUI_VM_PROJECT not found in {0}".format(filename)
        return root

    @classmethod
    def build_xml(self, element, parent):
        '''
        build a project tree recursive from given XML Element
        '''
        for subelement in element:
            xmltag = subelement.tag
            #create new nodes, if the xmltag describes a project nodes
            if (xmltag in self.inversed_names):
                classname = self.inversed_names[xmltag]
                glob_class = globals()[classname]
                #check if class is subclass of ProjectTreeNode
                #to avoid injection from xml
                if issubclass(glob_class, TreeNode):
                    node = glob_class(name='', parent=parent)
                else:
                    raise Exception('wrong class definition in xml file! '+
                                    "'{}' is unknown".format(classname))
                #assign attributes to node
                node.from_xml(subelement)
                #add child to project tree (resources handle this itself)
                if parent is not None:
                    parent.add_child(node)
                #recursion
                self.build_xml(subelement, node)

    @classmethod
    def write_xml(self, project_tree, filename):
        '''
        build XML ElementTree recursive
        out of project tree and write it to file

        Parameters
        ----------
        filename: String, xml file to write to, will be overwritten
        '''
        xml_tree = etree.Element('GUI_VM_PROJECT')
        project_tree.add_to_xml(xml_tree)
        etree.ElementTree(xml_tree).write(str(filename), pretty_print=True)

