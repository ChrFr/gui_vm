from resources import (H5Matrix, H5Table, H5Resource, Rule)

class TrafficModel(object):
    '''
    base class for traffic models
    '''
    def __init__(self, name):
        self.name = name
        #dictionary with categories of resources as keys
        #items are lists of the resources to this category
        self.resources = {}

    def process(self):
        pass

    def update(self, path):
        for resource in self.resources.values():
            resource.update(path)

    def get_resource(self, name):
        '''
        get a resource by name

        Parameters
        ----------
        name: String, name of the resource
        '''
        for res_name in self.resources:
            if res_name == name:
                return self.resources[res_name]
        return None

    def add_resources(self, *args):
        '''
        add a resource to the traffic model

        Parameters
        ----------
        resource: Resource
        '''
        for resource in args:
            self.resources[resource.name] = resource

    def is_complete(self):
        '''
        check if set of resources is complete (all sources are valid)
        '''
        for category in self.resources:
            for resource in self.resources[category]:
                if not resource.is_valid:
                    return False
        return True

class Maxem(TrafficModel):

    DEFAULT_SUBFOLDER = 'Maxem'
    def __init__(self, path=None, parent=None):
        super(Maxem, self).__init__('Maxem')
        self.subfolder = self.DEFAULT_SUBFOLDER

        self.apply_defaults()
        if path is not None:
            self.update()

    @property
    def n_zones(self):
        #number of zones is determined by the number of rows in
        #/zones/zones
        shape = self.resources['Zonendaten']\
                    .tables['/zones/zones'].shape
        if shape is None:
            return None
        else:
            return shape[0]

    @property
    def n_time_series(self):
        #time series is determined by the number of rows in
        #/activities/time_series
        shape = self.resources['Parameter']\
            .tables['/activities/time_series'].shape
        if shape is None:
            return None
        else:
            return shape[0]

    def apply_defaults(self):
        #### Parameters ####
        params = H5Resource('Parameter',
                            subfolder='params',
                            category='Parameter',
                            file_name='tdm_params.h5')
        time_series = H5Table('/activities/time_series')
                              #dtype="[('code', 'S8'), ('name', 'S30'), ('from_hour', 'i1'), ('to_hour', 'i1'), ('type', 'S8'), ('time_slice_durations', '<f4')]")
        params.add_tables(time_series)

        #### Constants ####
        constants = H5Resource('Konstanten',
                               subfolder='params',
                               category='Parameter',
                               file_name='tdm_constants.h5')

        #### Zonal data ####
        zonal_data = H5Resource('Zonendaten',
                                subfolder='zonal_data',
                                category='Zonen',
                                file_name='zonal_2010_bs_Innenstadt.h5')

        zones = H5Table('/zones/zones')
        rule = Rule('shape', '==', 'n_zones', reference=self)

        access_egress = H5Matrix('/zones/access_egress')
        binnenreisezeiten = H5Table('/zones/binnenreisezeiten')
        binnenreisezeiten.add_rule(rule)
        production = H5Table('/groups/production')
        production.add_rule(rule)
        activity_kf = H5Table('/activities/activity_kf')
        activity_kf.add_rule(rule)
        attraction = H5Table('/activities/attraction')
        attraction.add_rule(rule)

        zonal_data.add_tables(zones, binnenreisezeiten,
                              access_egress, production,
                              activity_kf, attraction)

        #### Skims #####
        skims_put = H5Resource('Skims Put',
                               subfolder='matrices\skims_put',
                               category='OV Matrizen',
                               file_name='VEP_NF_final_2010.h5')
        cost_put = H5Matrix('/put/cost_put')
        rule = Rule('shape', '==', ('n_time_series', 'n_zones', 'n_zones'),
                    reference=self)
        cost_put.add_rule(rule)
        skims_put.add_tables(cost_put)
        self.add_resources(params, constants, zonal_data, skims_put)

    def update(self, path):
        super(Maxem, self).update(path)


    def validate(self, path):
        self.update(path)
        for resource in self.resources:
            resource.is_valid()

    def process(self):
        pass
