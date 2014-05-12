from argparse import ArgumentParser
import os
import numpy as np
from backend import (H5Parser, InputTable, TableTable,
                     ArrayTable, ColumnTable, FileParser)

def main(folder, model):
    """

    Parameters
    ----------
    folder: String, name of the folder containing the
            input data (h5 files etc.)
    """
    file_names = [os.path.join(dp, f) for dp, dn, fn in os.walk(
        os.path.expanduser(folder)) for f in fn]
    input_table = InputTable()
    tables = TableTable()
    arrays = ArrayTable()
    columns = ColumnTable()

    #iterate over all files in directory (incl. subdirectories)
    for file_name in file_names:
        if file_name.endswith('.h5'):
            parser = H5Parser(file_name)
            i, t, a, c = parser.parse()
            tables += t
            arrays += a
            columns += c
        else:
            i = FileParser(file_name).parse()
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
