from argparse import ArgumentParser
import os
import numpy as np
from gui_vm.model.resource_dict import (ResourceConfigXMLParser)

def main(folder, model):
    """

    Parameters
    ----------
    folder: String, name of the folder containing the
            input data (h5 files etc.)
    """

    filenames = [os.path.join(dp, f) for dp, dn, fn in os.walk(
        os.path.expanduser(folder)) for f in fn]

    parser = ResourceConfigXMLParser()

    for filename in filenames:
        # the category is the path of the folder the file is in relative to the base folder (=subfolder)
        category = os.path.split(os.path.relpath(filename, folder))[0]

        if filename.endswith('.h5'):
            parser.add_h5_resource(filename, category=category)

    out = '{}.xml'.format(model)
    parser.write(os.path.join(folder, out))

if __name__ == "__main__":
    #    usage = """usage: python simulation_run.py [options] """
    parser = ArgumentParser()

    parser.add_argument("-f", "--folder",
                        action="store",
                        help="name of the folder containing the input data",
                        dest="folder", default='.')

    parser.add_argument("-m", "--model",
                        action="store",
                        help="name of traffic model",
                        dest="model", default='.')

    options = parser.parse_args()
    main(options.folder, options.model)
