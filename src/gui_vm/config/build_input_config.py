from argparse import ArgumentParser
import os
import numpy as np
from gui_vm.model.resource_dict import (H5ConfigParser, FileDict,
                                          TableDictArrayDict, ArrayDict, ColumnDict,
                                          ResourceConfigParser)


def main(folder, model):
    """

    Parameters
    ----------
    folder: String, name of the folder containing the
            input data (h5 files etc.)
    """
    filenames = [os.path.join(dp, f) for dp, dn, fn in os.walk(
        os.path.expanduser(folder)) for f in fn]
    input_table = FileDict()
    tables = TableDictArrayDict()
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
        input_table += i

    #write tables to csv
    input_out = '{}_input.csv'.format(model)
    tables_out = '{}_tables.csv'.format(model)
    arrays_out = '{}_arrays.csv'.format(model)
    columns_out = '{}_columns.csv'.format(model)
    if input_table.row_count > 0:
        input_table.to_csv(input_out)
    if tables.row_count > 0:
        tables.to_csv(tables_out)
    if arrays.row_count > 0:
        arrays.to_csv(arrays_out)
    if columns.row_count > 0:
        columns.to_csv(columns_out)

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
