from argparse import ArgumentParser
import os
import numpy as np
from gui_vm.model.resource_dict import (H5ConfigParser, FileDict,
                                        TableDict, ArrayDict, ColumnDict,
                                        ResourceConfigParser,
                                        ResourceConfigXMLParser)

def file_struct_to_csv(folder, model):
    filenames = [os.path.join(dp, f) for dp, dn, fn in os.walk(
        os.path.expanduser(folder)) for f in fn]

    inputs = FileDict()
    tables = TableDict()
    arrays = ArrayDict()
    columns = ColumnDict()

    #iterate over all files in directory (incl. subdirectories)
    for filename in filenames:
        if filename.endswith('.h5'):
            parser = H5ConfigParser(filename)
            i, t, a, c = parser.parse()
            tables += t
            arrays += a
            columns += c
        else:
            i = ResourceConfigParser(filename).parse()
        # the category is the path of the folder the file is in relative to the base folder (=subfolder)
        category = os.path.split(os.path.relpath(filename, folder))[0]
        i['category'] = category
        inputs += i

    #write tables to csv
    input_out = '{}_input.csv'.format(model)
    tables_out = '{}_tables.csv'.format(model)
    arrays_out = '{}_arrays.csv'.format(model)
    columns_out = '{}_columns.csv'.format(model)

    if inputs.row_count > 0:
        inputs.to_csv(os.path.join(folder, input_out))
    if tables.row_count > 0:
        tables.to_csv(os.path.join(folder, tables_out))
    if arrays.row_count > 0:
        arrays.to_csv(os.path.join(folder, arrays_out))
    if columns.row_count > 0:
        columns.to_csv(os.path.join(folder, columns_out))

def file_struct_to_xml(folder, model):

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


def main(folder, model):
    """

    Parameters
    ----------
    folder: String, name of the folder containing the
            input data (h5 files etc.)
    """

    file_struct_to_csv(folder, model)
    file_struct_to_xml(folder, model)

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
