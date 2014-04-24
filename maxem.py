from traffic_model import (TrafficModel, Resource)

DEFAULT_SUBFOLDER = 'Maxem'



class Maxem(TrafficModel):
    def __init__(self, parent=None):
        super(Maxem, self).__init__('Maxem')
        self.subfolder = DEFAULT_SUBFOLDER

        #important data
        self.n_zones = None
        self.n_time_series = None

        self.apply_defaults()

    def apply_defaults(self):
        params = Resource('Parameter',
                          subfolder='params',
                          category='Parameter',
                          default='tdm_params.h5')
        constants = Resource('Konstanten',
                             subfolder='params',
                             category='Parameter',
                             default='tdm_constants.h5')
        zones = Resource('Zonendaten',
                         subfolder='zonal_data',
                         category='Zonen',
                         default='zonal_2010_bs_Innenstadt.h5')

        self.add_resource(params)
        self.add_resource(constants)
        self.add_resource(zones)

    def validate(self):
        pass

    def process(self):
        pass
