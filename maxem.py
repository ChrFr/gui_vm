from traffic_model import (TrafficModel, H5Resource, H5Matrix, H5Table)

DEFAULT_SUBFOLDER = 'Maxem'


class Maxem(TrafficModel):
    def __init__(self, path=None, parent=None):
        super(Maxem, self).__init__('Maxem')
        self.subfolder = DEFAULT_SUBFOLDER

        #important data
        self.n_zones = None
        self.n_time_series = None

        self.apply_defaults()
        if path is not None:
            self.update()

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
        access_egress = H5Matrix('/zones/access_egress')
        binnenreisezeiten = H5Table('/zones/binnenreisezeiten')
        production = H5Table('/groups/production')
        activity_kf = H5Table('/activities/activity_kf')
        attraction = H5Table('/activities/attraction')

        zonal_data.add_tables(zones, binnenreisezeiten,
                              access_egress, production,
                              activity_kf, attraction)

        #### Skims #####
        skims_put = H5Resource('Skims Put',
                               subfolder='matrices\skims_put',
                               category='OV Matrizen',
                               file_name='VEP_NF_final_2010.h5')
        cost_put = H5Matrix('/put/cost_put')
        cost_put.add_rules(shape=('n_time_series', 'n_zones', 'n_zones'),
                           operator='==',
                           reference=self)
        skims_put.add_tables(cost_put)
        self.add_resources(params, constants, zonal_data, skims_put)

    def update(self, path):
        super(Maxem, self).update(path)
        #time series is determined by the number of rows in
        #/activities/time_series
        shape = self.resources['Parameter']\
            .tables['/activities/time_series'].shape
        if shape is None:
            self.n_time_series = None
        else:
            self.n_time_series = shape[0]
        #number of zones is determined by the number of rows in
        #/zones/zones
        shape = self.resources['Zonendaten']\
                    .tables['/zones/zones'].shape
        if shape is None:
            self.n_zones = None
        else:
            self.n_zones = shape[0]

    def validate(self, path):
        self.update(path)
        for resource in self.resources:
            resource.is_valid()

    def process(self):
        pass
