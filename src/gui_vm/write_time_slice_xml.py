# -*- coding: utf8 -*-
#------------------------------------------------------------------------------
# Name:        VISUM Matrices to HDF5 for each time
# Purpose:     Berechnet ÖV Kenngrößen nach vordefiniertem Verfahrem und Zeitscheiben
#              Speichert alle Kenngrößenmatrizen je berechneter Zeitscheibe in HDF5 Datei
#              -> nicht berechnete Matrizen erhalten in jeder Zeitscheibe den zuvor berechneten Wert
#
# Author:      Nina Kohnen
#
# Created:     03.04.2013
# Copyright:   (c) Barcelona 2013
# Licence:     <your licence>
#------------------------------------------------------------------------------

import tables
import os
import tempfile
from argparse import ArgumentParser
from lxml import etree
import sys

from tables.exceptions import NoSuchNodeError

from gui_vm.get_param_from_config import Params


class GetTimeSclices(object):

    def __init__(self, project_folder, scenario_name):
        self.project_folder = project_folder
        self.scenario_name = scenario_name
        project_xml = os.path.join(project_folder, 'project.xml')
        params = Params(project_xml)
        self.h5_params_file = params.get_params_of_scenario(scenario_name,
                                                            ('Params', ))[0].file_absolute

    def import_time_series(self):
        with tables.openFile(self.h5_params_file) as h:
            try:
                time_series = h.root.activities.time_series[:]
            except NoSuchNodeError:
                msg = 'No table activities.time_series defined in {}'
                raise NoSuchNodeError(msg.format(self.h5_params_file))
            if not len(time_series):
                msg = 'table activities.time_series in {} is empty'
                raise ValueError(msg.format(self.h5_params_file))
        self.add_xml(time_series)

    def add_xml(self, time_series):
        """create time interval xml and import into Visum"""
        time_intervals = []
        d = {'FUNCTIONS': {
                 'ANALYSISTIMES': {'ENDDAYINDEX': '1',
                                    'STARTDAYINDEX': '1',
                                    'USEONPRTRESULTS': '1',
                                    'USEONPUTRESULTS': '1'},
                 'ANALYSISTIMEINTERVAL': time_intervals, }
             }
        codes = []
        for t, ts in enumerate(time_series):
            ti = self.add_time_interval(ts['from_hour'],
                                        ts['to_hour'],
                                        codes,
                                        code=ts['code'])

            time_intervals.append(ti)
        aggr_ti = self.add_time_interval(time_series[0]['from_hour'],
                                         time_series[-1]['to_hour'],
                                         codes,
                                         is_aggregate=True)
        time_intervals.append(aggr_ti)

        # write xml to tempfile
        xml = self.to_xml(d)
        print(etree.tostring(xml, pretty_print=True))

    def to_xml(self, d):
        procedures = etree.Element('PROCEDURES')
        doc = etree.ElementTree(element=procedures)
        self.add_subtree(procedures, d)
        return doc

    def add_attribute(self, parent, key, value):
        parent.attrib[key] = value

    def add_subtree(self, parent, elem):
        for key, value in elem.iteritems():
            if isinstance(value, dict):
                child = etree.SubElement(parent, key)
                self.add_subtree(child, value)
            elif isinstance(value, list):
                for member in value:
                    self.add_subtree(parent, member)
            else:
                self.add_attribute(parent, key, value)


    def add_time_interval(self,
                          starttime,
                          endtime,
                          codes,
                          is_aggregate=False,
                          code=None):
        """
        create xml-code for time interval

        Parameters
        ----------
        starttime : int
        endtime : int
        codes : list
        is_aggregate : bool (optional, default=False)
        code : str, optional
            if not given, it will be derived from the start- and endtime
        """
        if code is None:
            code = '{st:02d}{et:02d}'.format(st=starttime, et=endtime)
        name = '{st:02d}h-{et:02d}h'.format(st=starttime, et=endtime)
        et = '{et:02d}:59:59'.format(et=endtime - 1)
        st = '{st:02d}:00:00'.format(st=starttime)
        if is_aggregate:
            ISAGGREGATE = '1'
            DERIVEDFROM = ','.join(codes)
            AGGRFUNCTION = 'SUM'

        else:
            ISAGGREGATE = '0'
            DERIVEDFROM = ''
            AGGRFUNCTION = 'MEAN'


        ti = {'ANALYSISTIMEINTERVAL':
              {'AGGRFUNCTION': AGGRFUNCTION,
               'CODE': code,
               'DERIVEDFROM': DERIVEDFROM,
               'ENDDAYINDEX': '1',
               'ENDTIME': et,
               'ISAGGREGATE': ISAGGREGATE,
               'NAME': name,
               'STARTDAYINDEX': '1',
               'STARTTIME': st,
               }}

        if not is_aggregate:
            codes.append(code)
        return ti


if __name__ == '__main__':
    parser = ArgumentParser(description="Parameter Importer")

    parser.add_argument("-f", action="store",
                        help="Projektordner mit XML-Projektdatei",
                        dest="project_folder", default=None)

    parser.add_argument("-s", action="store",
                        help="Zeitscheiben für angegebenes Szenario ausgeben",
                        dest="scenario_name", default=None)

    options = parser.parse_args()

##    calcMatrix = CalcMatrix.fromProjectFile(options.project_folder,
##                                            options.scenario_name,
##                                            options.pythonpath)
    get_time_slices = GetTimeSclices(options.project_folder,
                                     options.scenario_name)
    get_time_slices.import_time_series()
