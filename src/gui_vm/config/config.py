from lxml import etree
import os, sys
import gui_vm
import copy

CONFIG_FILE = "config.xml"

# holds structure of settings and default values
# you may change sth in this structure 2 levels deep (eg adding a trafficmodel)
# (deeper changes are not recognized when loading xml settings from previous versions -> delete config.xml)
setting_struct = {
    'environment': {
        'hdf5_viewer': ''
        },
    'auto_check': False,
    'trafficmodels': {
        'Maxem': {
            'default_folder': '', # folder with default resources
            'executable': 'python.exe', # path to file that executes the model (respectively the interpreter, virtual machine etc.)
            'arguments': '-m tdmks.main_xml', # command line arguments for the executable
            'class_module': 'gui_vm.model.maxem.maxem' # the module with gui_vm related trafficmodel definitions (represents the gui_vm src folder structure)
            },
        'Wiver': {
            'default_folder': '',
            'executable': '',
            'arguments': '',
            'class_module': 'gui_vm.model.wiver.wiver'
            },
    },
    'history': [],
}


class Singleton(type):
    '''
    Singleton metaclass
    '''
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Config():
    '''
    holds informations about the environment and traffic model settings
    '''
    __metaclass__ = Singleton

    def __init__(self):
        main_p = gui_vm.__path__[0]
        folder = os.path.join(os.environ['APPDATA'], 'gui_vm')
        self.filename = os.path.join(folder, CONFIG_FILE)
        self.mainWindow = None
        self.batch_mode = False
        self.admin_mode = False
        self.save_disabled = False
        self.settings = {}
        self.read()

    def add_to_history(self, project_folder):
        h = self.settings['history']
        # try to remove first to avoid double entries if already in history
        self.remove_from_history(project_folder)
        h.insert(0, project_folder)
        if len(h) > 10:
            self.settings['history'] = h[:10]
        self.write()

    def remove_from_history(self, project_folder):
        h = self.settings['history']
        try:
            h.remove(project_folder)
        except:
            pass
        self.write()

    '''
    read the config from given xml file (default config.xml)
    recognizes changes in setting_struct 2 levels deep (if you add or change
    sth in comparsion to older settings)
    '''
    def read(self, filename=None):
        if not filename:
            filename = self.filename
        if not os.path.isfile(filename):
            self.reset()
        tree = etree.parse(filename)
        self.settings = copy.deepcopy(setting_struct)
        f_set = xml_to_dict(tree.getroot(), ['history'])
        for key, value in f_set.iteritems():
            if isinstance(value, dict):
                self.settings[key].update(value)
            else:
                self.settings[key] = value

    '''
    write the config as xml to given file (default config.xml)
    '''
    def write(self, filename=None):
        xml_tree = etree.Element('CONFIG')
        dict_to_xml(xml_tree, self.settings)
        if not filename:
            filename = self.filename
        etree.ElementTree(xml_tree).write(str(filename), pretty_print=True)

    def reset(self):
        '''
        resets the config to the values in setting_struct
        '''
        #keep the history
        hist_tmp = self.settings['history'] if 'history' in self.settings else []
        self.settings = copy.deepcopy(setting_struct)
        self.settings['history'] = hist_tmp
        self.write()

'''
append the entries of a dictionary as childs to the given xml tree element
'''
def dict_to_xml(element, dictionary):
    if isinstance(dictionary, list):
        for value in dictionary:
            elem = etree.Element('value')
            element.append(elem)
            if isinstance(dictionary, list) or isinstance(dictionary, dict):
                dict_to_xml(elem, value)
    elif not isinstance(dictionary, dict):
        element.text = str(dictionary)
    else:
        for key in dictionary:
            elem = etree.Element(key)
            element.append(elem)
            dict_to_xml(elem, dictionary[key])

'''
convert a xml tree to a dictionary
represented_as_arrays: list of Strings, all XML Tags, which should be handled as arrays
'''
def xml_to_dict(tree, represented_as_arrays):
    if tree.tag in represented_as_arrays:
        value = []
        for child in tree.getchildren():
            value.append(xml_to_dict(child, represented_as_arrays))
    elif len(tree.getchildren()) > 0:
        value = {}
        for child in tree.getchildren():
            value[child.tag] = xml_to_dict(child, represented_as_arrays)
    else:
        value = tree.text
        if not value:
            value = ''
        elif value == 'False':
            value = False
        elif value == 'True':
            value = True
    return value
