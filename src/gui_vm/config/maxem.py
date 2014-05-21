from gui_vm.model.traffic_model import TrafficModel
from gui_vm.model.resources import Rule
from collections import OrderedDict
import os

class Maxem(TrafficModel):
    '''
    Maxem traffic model
    '''

    #names of the config files containing the target status of all input data
    #relative to the directory this file is in
    INPUT_CONFIG_FILE = 'Maxem_input.csv'
    TABLES_CONFIG_FILE = 'Maxem_tables.csv'
    ARRAYS_CONFIG_FILE = 'Maxem_arrays.csv'
    COLUMNS_CONFIG_FILE = 'Maxem_columns.csv'

    #names of the fields that can be displayed outside the model
    monitored = OrderedDict([('n_zones', 'Anzahl Zonen'),
                             ('n_time_series', 'Anzahl Zeitscheiben'),
                             ('n_activity_pairs', 'Aktivitaetenpaare'),
                             ('activity_names', 'Aktivitaeten'),
                             ('activity_codes', 'Aktivitaetencodes')])

    def __init__(self, path=None):
        input_config_file = os.path.join(os.path.dirname(__file__),
                                         self.INPUT_CONFIG_FILE)
        tables_config_file = os.path.join(os.path.dirname(__file__),
                                         self.TABLES_CONFIG_FILE)
        arrays_config_file = os.path.join(os.path.dirname(__file__),
                                         self.ARRAYS_CONFIG_FILE)
        columns_config_file = os.path.join(os.path.dirname(__file__),
                                         self.COLUMNS_CONFIG_FILE)
        super(Maxem, self).__init__(
            'Maxem',
            input_config_file=input_config_file,
            tables_config_file=tables_config_file,
            arrays_config_file=arrays_config_file,
            columns_config_file=columns_config_file)

        self.read_config()

        ####special rules for the maxem model#####

        #track the activities
        activities = self.resources['Params'].get_child('activities')
        activities.get_child('code').track_content = True
        activities.get_child('name').track_content = True

        attraction = self.resources['Zonen'].get_child('attraction')
        activity_track = ActivityTracking('column_names', 'ZP_?',
                                          'activity_codes', reference=self)
        attraction.add_rule(activity_track)

        activity_kf = self.resources['Zonen'].get_child('activity_kf')
        activity_track = ActivityTracking('column_names', 'KF_?',
                                          'activity_codes', reference=self)
        activity_kf.add_rule(activity_track)

        if path is not None:
            self.update()

    def __del__(self):
        print 'traffic model deleted'


    @property
    def n_zones(self):
        #number of zones is determined by the number of rows in
        #/zones/zones
        shape = self.resources['Zonen'].get_child('zones').shape
        if shape is None:
            return None
        else:
            return int(shape[0])

    @property
    def n_time_series(self):
        #time series is determined by the number of rows in
        #/activities/time_series
        shape = self.resources['Params'].get_child('time_series').shape
        if shape is None:
            return None
        else:
            return int(shape[0])

    @property
    def n_activity_pairs(self):
        shape = self.resources['Params'].get_child('activitypairs').shape
        if shape is None:
            return None
        else:
            return int(shape[0])

    @property
    def activity_codes(self):
        activities = self.resources['Params'].get_child('activities')
        return activities.get_child('code').content

    @property
    def activity_names(self):
        activities = self.resources['Params'].get_child('activities')
        return activities.get_child('name').content

    def update(self, path):
        super(Maxem, self).update(path)

    def process(self):
        pass


class ActivityTracking(Rule):
    '''
    special rule to determine if the activity codes are represented in
    a table

    Parameter
    --------
    field_name: String, name of the field that contains the column names
    identifier: String, common name of the columns, the ? will be replaced
                with the activity code
    referenced_field: String, name of the field of the referenced object that
                      holds the activities
    reference: object, the object that holds the activities
    '''

    def __init__(self, field_name, identifier, referenced_field, reference):
        self.identifier = identifier
        super(ActivityTracking, self).__init__(field_name, referenced_field,
                                               self.is_in, reference=reference)

    def is_in(self, column_names, activity_list):
        '''
        check if activity is represented in the columns
        '''
        if activity_list is None:
            return False, 'Aktivitaet nicht definiert'
        #make activity list iterable (e.g. if only one activity)
        if not hasattr(activity_list, '__iter__'):
            activity_list = [activity_list]

        for activity in activity_list:
            col_name = self.identifier
            col_name = col_name.replace('?', activity)
            if col_name not in column_names:
                return False, 'Spalte {} fehlt'.format(col_name)
        return True