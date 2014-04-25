from copy import deepcopy
import os
import time
from lxml import etree
from shutil import copytree
from config import DEFAULT_FOLDER

from maxem import Maxem
TRAFFIC_MODELS = ['Maxem']

#dictionary defines how classes are called when written to xml
#also used while reading xml project config
XML_CLASS_NAMES = {'SimRun': 'Szenario',
                   'Project': 'Projekt',
                   'ResourceNode': 'Ressource',
                   'ProjectTreeNode': 'Layer'}

inversed_names = {v:k for k, v in XML_CLASS_NAMES.items()}


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
        xml_element = etree.SubElement(parent,
                                       XML_CLASS_NAMES[self.__class__.__name__])
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
    def __init__(self, model, name=None, parent=None):
        super(SimRun, self).__init__(name, parent=parent)
        self._available = TRAFFIC_MODELS
        self.set_model(model)
        #simulation runs can be renamed
        self.rename = True

    @property
    def path(self):
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
        set the traffic model of the sim run
        '''
        if name in self._available:
            self.model = globals()[name]()
            self.model.set_path(self.path)
            #remove the old children of the sim run (including resources)
            for i in reversed(range(self.child_count())):
                self.remove_child_at(i)

            #categorize resources
            res_dict = {}
            resources = self.model.resources.values()
            for resource in resources:
                if not res_dict.has_key(resource.category):
                    res_dict[resource.category] = []
                res_dict[resource.category].append(resource)
            #add the resources needed by the traffic model, categorized
            for category in res_dict:
                layer_node = ProjectTreeNode(category)
                self.add_child(layer_node)
                for resource in res_dict[category]:
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
        for subelement in element:
            if subelement.tag == 'Verkehrsmodell':
                name = subelement.text
                if name in self._available:
                    self.model = globals()[name]()
                else:
                    raise Exception(
                        'Traffic Model {0} not available'.format(name))


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
    def __init__(self, name, resource=None,
                parent=None):
        if resource is None:
            resource = Resource(name)
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
            xml_element, 'Dateiname').text = self.resource.file_name
        etree.SubElement(
            xml_element, 'Dateipfad').text = self.resource.file_path

    def from_xml(self, element):
        '''
        read the basic attributes from element and assign them to the node

        Parameters
        ----------
        element: SubElement,
                 xml node containing informations about this project node
        '''
        super(ResourceNode, self).from_xml(element)
        self.resource = Resource(self.name)
        for subelement in element:
            if subelement.tag == 'Dateiname':
                self.resource.file_name = subelement.text
            if subelement.tag == 'Dateipfad':
                self.resource.file_path = subelement.text

    @property
    def note(self):
        '''
        short textual info to display in ui tree

        Return
        ------
        String
        '''
        source = self.source
        if source is None:
            source = 'nicht vorhanden'
        note = '<{}>'.format(source)
        return note

    @property
    def source(self):
        '''
        Return
        ------
        path of the resource file within the project folder
        '''
        if self.resource.file_name is None:
            return None
        else:
            source = os.path.join(self.resource.subfolder,
                                  self.resource.file_name)
            return source

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
        #####hard copy missing by now#####
        self.original_source = filename

#class Layer(ProjectTreeNode):
    #'''
    #category to structure the project tree (especially the resources)
    #contains no further information

    #Parameters
    #----------
    #name: String, the name the category gets
    #'''
    #def __init__(self, name, parent=None):
        #super(Layer, self).__init__(name, parent=parent)

    #def add_to_xml(self, parent):
        #'''
        #converts all needed information of this node and recursive of
        #its children to xml and attaches it to the given parent

        #Parameters
        #----------
        #parent: SubElement,
                #this node will be added to it
        #'''
        #xml_element = etree.SubElement(parent,
                                       #XML_NAMES[self.__class__.__name__])
        #xml_element.attrib['name'] = self.name
        #for child in self.children:
            #child.add_to_xml(xml_element)

class XMLParser(object):
    '''
    class that holds functions to read and write xml
    '''
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
            if xmltag in inversed_names:
                classname = inversed_names[xmltag]
                node = globals()[classname]('')
                #assign attributes to node
                node.from_xml(subelement)
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
