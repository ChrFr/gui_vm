from lxml import etree

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
        self.filename = "./config/config.xml"
        self.default_file = "./config/default_config.xml"
        self.settings = {
            'environment': {
                'python_path': '',
                },

            'trafficmodels': {
                'Maxem': {
                    'default_folder': '',
                    'executable': ''
                    },
                'VerkMod': {
                    'default_folder': '',
                    'executable': ''
                    }
            }
        }

    '''
    read the config from given xml file (default config/config.xml)
    '''
    def read(self, filename=None):
        if not filename:
            filename = self.filename
        tree = etree.parse(filename)
        self.settings = xml_to_dict(tree.getroot())

    '''
    write the config as xml to given file (default config/config.xml)
    '''
    def write(self, filename=None):
        xml_tree = etree.Element('CONFIG')
        dict_to_xml(xml_tree, self.settings)
        if not filename:
            filename = self.filename
        etree.ElementTree(xml_tree).write(str(filename), pretty_print=True)

'''
append the entries of a dictionary as childs to the given xml tree element
'''
def dict_to_xml(element, dictionary):
    if not isinstance(dictionary, dict):
        element.text = str(dictionary)
    else:
        for key in dictionary:
            elem = etree.Element(key)
            element.append(elem)
            dict_to_xml(elem, dictionary[key])

'''
convert a xml tree to a dictionary
'''
def xml_to_dict(tree):
    if len(tree.getchildren()) > 0:
        value = {}
        for child in tree.getchildren():
            value[child.tag] = xml_to_dict(child)
    else:
        value = tree.text
        if not value:
            value = ''
    return value
