from copy import deepcopy
import os
import time
from lxml import etree
from shutil import copytree
from gui_vm.config.config import DEFAULT_FOLDER
from resources import ResourceFile
from gui_vm.config.maxem import Maxem

TRAFFIC_MODELS = ['Maxem']

#dictionary defines how classes are called when written to xml
#also used while reading xml project config
XML_CLASS_NAMES = {'SimRun': 'Szenario',
                   'Project': 'Projekt',
                   'ResourceNode': 'Ressource',
                   'ProjectTreeNode': 'Layer'}


class ProjectTreeNode(object):
    '''
    Base class of nodes in the project tree
    '''
    def __init__(self, name, parent=None):
        self.parent = parent
        self.name = name
        self.children = []
        self.rename = False

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

    def find_all_by_classname(self, classname):
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
            print '{}: {}'.format(self.name, self.__class__.__name__)
            if self.__class__.__name__ == classname:
                children.extend([self])
            for child in self.children:
                children.extend(child.find_all_by_classname(classname))
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
        if len(self.children) == 0:
            return None
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


class SimRun(ProjectTreeNode):
    '''
    Node that holds informations about the a simulation run (e.g. the
    used traffic model)
    the resources are its children
    '''
    def __init__(self, model=None, name=None, parent=None):
        super(SimRun, self).__init__(name, parent=parent)
        self._available = TRAFFIC_MODELS
        if model is not None:
            self.set_model(model)
        #simulation runs can be renamed
        self.rename = True

    @property
    def meta(self):
        return self.model.characteristics

    def get_resource(self, name):
        '''
        get a resource node by name

        Parameters
        ----------
        name: String, name of the resource
        '''
        found = simrun.find_all(self.name)
        res_nodes = []
        for node in found:
            if isinstance(node, ResourceNode):
                res_nodes.append(node)
        if len(res_nodes) > 2:
            raise Exception('Multiple Definition of resource {}'
                            .format(self.name))
        return res_nodes[0]

    @property
    def path(self):
        if self.get_parent_by_class(Project).project_folder is None:
            return None
        return os.path.join(
            self.get_parent_by_class(Project).project_folder, self.name)

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
        set the traffic model of the sim run, create new traffic model and
        integrate it into the project tree

        Parameters
        ----------
        name: String, name of the traffic model
        '''
        if name in self._available:
            self.model = globals()[name]()
            self.model.update(self.path)
            #remove the old children of the sim run (including resources)
            for i in reversed(range(self.child_count())):
                self.remove_child_at(i)

            #categorize resources
            res_dict = {}
            resources = self.model.resources.values()
            for resource in resources:
                if not res_dict.has_key(resource.subfolder):
                    res_dict[resource.subfolder] = []
                res_dict[resource.subfolder].append(resource)
            #add the resources needed by the traffic model, categorized
            for subfolder in res_dict:
                layer_node = ProjectTreeNode(subfolder)
                self.add_child(layer_node)
                for resource in res_dict[subfolder]:
                    layer_node.add_child(ResourceNode(resource.name,
                                                      resource=resource,
                                                      parent=self))
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
        xml_element = super(SimRun, self).add_to_xml(parent)
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
        super(SimRun, self).from_xml(element)
        #init the traffic model before resources can be set
        vm = element.find('Verkehrsmodell').text
        if vm in self._available:
            self.model = globals()[vm]()
            self.model.update(self.path)
        else:
            raise Exception('Traffic Model {0} not available'.format(name))


class Project(ProjectTreeNode):
    '''
    Node that holds the informations about the project
    the simulation runs and their resources are its children
    '''
    def __init__(self, name, parent=None):
        super(Project, self).__init__(name, parent=parent)
        self.project_folder = os.getcwd()
        self.meta = {}
        #projects can be renamed
        self.rename = True
        self.meta['Datum'] = time.strftime("%d.%m.%Y")
        self.meta['Uhrzeit'] = time.strftime("%H:%M:%S")
        self.meta['Autor'] = ''

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
        folder = etree.Element('Projektordner')
        folder.text = self.project_folder
        xml_element.insert(0, folder)

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
            if subelement.tag == 'Projektordner':
                self.project_folder = subelement.text

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

    def add_run(self, model, name=None):
        if name is None:
            name = 'Szenario {}'.format(self.child_count())
        #copytree(os.path.join(DEFAULT_FOLDER, 'Maxem'),
                 #os.path.join(self.project_folder, name))
        new_run = SimRun(model, name, parent=self)
        self.add_child(new_run)

    def remove_run(self, name):
        self.remove_child(name)


class ResourceNode(ProjectTreeNode):
    '''
    wrap a resource in a node

    Parameters
    ----------
    resource: Resource,
              resource of the traffic model
    '''
    def __init__(self, name, resource=None,
                 parent=None):
        self.resource = resource
        super(ResourceNode, self).__init__(name, parent=parent)
        self.original_source = self.full_source

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
        simrun = self.get_parent_by_class(SimRun)
        self.resource = ResourceFile(self.name)
        if simrun is not None:
            existing_resource = simrun.model.get_resource(self.name)
            #if resource is defined by traffic model -> get it
            if existing_resource is not None:
                self.resource = existing_resource
        self.original_source = element.find('Quelle').text
        source = element.find('Projektdatei').text
        if source is None:
            source = ''
        self.source = source

    @property
    def model(self):
        return self.get_parent_by_class(SimRun).model

    @property
    def simrun_path(self):
        return self.get_parent_by_class(SimRun).path

    @property
    def note(self):
        '''
        short textual info to display in ui tree

        Return
        ------
        String
        '''
        file_name = self.resource.file_name
        if file_name is None or file_name == '':
            file_name = 'nicht gesetzt'
        note = '<{}>'.format(file_name)
        return note

    @property
    def source(self):
        '''
        Return
        ------
        path of the resource file within the project folder
        '''
        if (self.resource is None or
            self.resource.file_name is None or
            self.resource.file_name == ''):
            return None
        source = os.path.join(self.resource.subfolder,
                              self.resource.file_name)
        return source

    @property
    def full_path(self):
        return os.path.join(self.run_path, self.resource.subfolder)

    @source.setter
    def source(self, subpath):
        subfolder, filename = os.path.split(subpath)
        #only set filename, because subfolder will be determined
        #by the category
        self.resource.set_source(filename)
        #self.resource.update(self.simrun_path)

    @property
    def full_source(self):
        '''
        Return
        ------
        full path of the resource file
        '''
        #join path with simrun path to get full source
        source = self.source
        if self.source is not None:
            source = os.path.join(
                self.run_path, self.source)
        return source

    @property
    def run_path(self):
        return self.get_parent_by_class(SimRun).path

    def set_source(self, filename):
        '''
        set the path and filename of the resource

        Parameters
        ----------
        filename: String, path + name of file
        '''
        self.original_source = filename
        #####hard copy missing by now#####
        self.source = filename

    def update(self):
        self.resource.update(self.run_path)


class XMLParser(object):
    '''
    class that holds functions to read and write xml
    '''
    inversed_names = {v: k for k, v in XML_CLASS_NAMES.items()}

    def __init__(self):
        pass

    @classmethod
    def read_xml(self, rootname, filename):
        tree = etree.parse(filename)
        root_element = tree.getroot()
        if root_element.tag == 'GUI_VM':
            root = ProjectTreeNode(root_element.tag)
            self.build_xml(root_element, root)
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
                node = globals()[classname](name='', parent=parent)
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
        xml_tree = etree.Element('GUI_VM')
        project_tree.add_to_xml(xml_tree)
        etree.ElementTree(xml_tree).write(str(filename), pretty_print=True)
