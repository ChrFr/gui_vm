# -*- coding: utf-8 -*-
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
        
    def add_special_attributes(self):
        '''
        adds empty Monitor and RunOptions as required by gui_vm including comments
        '''
        monitor = etree.SubElement(self.root, 'Monitor')
        comment = etree.Comment('observed attributes, can be cross referenced to from other resources via definitions with {nameofmonitorobject},\n' + 
                                'order of monitored attributes determines the order in which they will be shown in GUI Scenario details')
        monitor.insert(1, comment)
        comment = etree.Comment('==== possible entries ====')
        monitor.insert(2, comment)
        comment = etree.Comment('<shape alias="" resource="" path="/">nameofmonitorobject</shape>\n'
                                'observes the shape of a table, may be referenced like this: <H5Array dimension="{nameofmonitorobject} x {nameofmonitorobject} x 10" ... />')
        monitor.insert(3, comment)
        comment = etree.Comment('<content alias="" resource="" path="/" column="">nameofmonitorobject</shape>\n'
                                'observes the content of a column, may be referenced like this: <column ... > text{nameofmonitorobject}text </column>')
        monitor.insert(4, comment)
        runoptions = etree.SubElement(self.root, 'RunOptions')
        comment = etree.Comment('selectable options before running, values may reference monitored content \n' +
                                'is_unique - only one option can be checked at a time,\n' +
                                'default - by default selected option (index),\n' +
                                'is_special_only - only available for special runs,\n' +
                                'is_primary_only - only available for primary runs\n' +
                                'e.g. <group name="detailed" is_special_only="True">\n' +
                                '   <option value="groups">Gruppendetails</option>\n' +
                                u'   <option value="activities">Aktivitätendetails</option>\n' +
                                '</group>' )
        runoptions.insert(1, comment)

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
            tclass =  table._c_classId
            if tclass == 'TABLE':
                table_xml = etree.SubElement(res_xml, table_type)
                table_xml.attrib['subdivision'] = table._v_pathname
                table_xml.attrib['n_rows'] = str(table.nrows)
                table_data = table.read()
                columns = table_data.dtype
                for col in columns.names:
                    col_xml = etree.SubElement(table_xml, 'column')
                    col_xml.text = col
                    col_xml.attrib['type'] = str(columns[col])

                    # following attributes have to be set manually!
                    col_xml.attrib['minimum'] = ''
                    col_xml.attrib['maximum'] = ''
                    col_xml.attrib['is_primary_key'] = '0'

            elif tclass == 'ARRAY' or tclass == 'UNIMPLEMENTED':
                table_xml = etree.SubElement(res_xml, table_type)
                table_xml.attrib['path'] = table._v_pathname
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
