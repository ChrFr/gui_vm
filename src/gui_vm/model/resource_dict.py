from collections import OrderedDict
import csv
import numpy as np
import os
from backend import HDF5
from lxml import etree

class ResourceConfigXMLParser(object):
    '''
    parser specifically for HDF5 files and their nodes
    '''
    def __init__(self):
        self.root = etree.Element('Resources')

    def add_h5_resource(self, filename, category=''):
        directory, fname = os.path.split(filename)
        res_xml = etree.SubElement(self.root, 'H5Resource')
        res_xml.attrib['name'] = os.path.splitext(fname)[0]
        res_xml.attrib['category'] = category

        h5_input = HDF5(filename)
        h5_input.read()
        for table in h5_input.h5_file:
            #in_table = FileDict()
            #in_table['resource_name'] = name
            table_type = 'H5{}'.format(table._c_classId.title())
            if table._c_classId == 'TABLE':
                table_xml = etree.SubElement(res_xml, table_type)
                table_xml.attrib['subdivision'] = table._v_pathname
                table_xml.attrib['n_rows'] = str(table.nrows)
                table_data = table.read()
                columns = table_data.dtype
                for col in columns.names:
                    col_xml = etree.SubElement(table_xml, 'column')
                    col_xml.attrib['name'] = col
                    col_xml.attrib['type'] = str(columns[col])

                    # following attributes have to be set manually!
                    col_xml.attrib['minimum'] = ''
                    col_xml.attrib['maximum'] = ''
                    col_xml.attrib['is_primary_key'] = '0'

            elif table._c_classId == 'ARRAY':
                table_xml = etree.SubElement(res_xml, table_type)
                table_xml.attrib['subdivision'] = table._v_pathname
                shape = table.shape
                dim = ''
                for d in shape:
                    dim += '{} x '.format(d)
                dim = dim[:-3]
                table_xml.attrib['dimension'] = dim

                # following attributes have to be set manually!
                table_xml.attrib['minimum'] = ''
                table_xml.attrib['maximum'] = ''
            else:
                continue

    def write(self, filename):
        etree.ElementTree(self.root).write(str(filename), pretty_print=True)

    def read(self, filename):
        self.root = etree.parse(filename)
