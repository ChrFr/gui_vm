from lxml import etree

class Config():
    def __init__(self):
        self.filename = "config/config.xml"
        self.default_file = "config/default_config.xml"
        self.settings = {
            'environment': {
                'default_project_folder': '',
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

    def read(self, filename=None):
        if not filename:
            filename = self.filename
        tree = etree.parse(filename)
        self.settings = xml_to_dict(tree.getroot())

    def write(self, filename=None):
        xml_tree = etree.Element('CONFIG')
        dict_to_xml(xml_tree, self.settings)
        if not filename:
            filename = self.filename
        etree.ElementTree(xml_tree).write(str(filename), pretty_print=True)

def dict_to_xml(element, dictionary):
    if not isinstance(dictionary, dict):
        element.text = str(dictionary)
    else:
        for key in dictionary:
            elem = etree.Element(key)
            element.append(elem)
            dict_to_xml(elem, dictionary[key])

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
