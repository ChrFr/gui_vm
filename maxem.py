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
        params = H5Resource('Parameter',
                            subfolder='params',
                            category='Parameter',
                            file_name='tdm_params.h5')
        time_series = H5Table('/activities/time_series', "[('code', 'S8'), ('name', 'S30'), ('from_hour', 'i1'), ('to_hour', 'i1'), ('type', 'S8'), ('time_slice_durations', '<f4')]")
        params.add_table(time_series)
        constants = H5Resource('Konstanten',
                               subfolder='params',
                               category='Parameter',
                               file_name='tdm_constants.h5')
        zones = H5Resource('Zonendaten',
                           subfolder='zonal_data',
                           category='Zonen',
                           file_name='zonal_2010_bs_Innenstadt.h5')
        skims_put = H5Resource('Skims Put',
                               subfolder='matrices\skims_put',
                               category='OV Matrizen',
                               file_name='VEP_NF_final_2010.h5')
        cost_put = H5Matrix('/put/cost_put')
        skims_put.add_table(cost_put)

        self.add_resources(params, constants, zones, skims_put)

    def update(self, path):
        self.set_path(path)
        self.n_zones = self.resources['Parameter']\
            .tables['/activities/time_series'].shape[0]

    def validate(self, path):
        self.update(path)
        dtype_ = [('code', 'S8'), ('name', 'S30'), ('from_hour', 'i1'), ('to_hour', 'i1'), ('type', 'S8'), ('time_slice_durations', '<f4')]

    def process(self):
        pass
