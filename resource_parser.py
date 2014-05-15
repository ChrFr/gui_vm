from collections import OrderedDict
import csv
import numpy as np

INPUT_HEADER = ['resource_name', 'subdivision', 'category', 'type']
TABLE_HEADER = ['resource_name', 'subdivision', 'n_rows']
ARRAY_HEADER = ['resource_name', 'subdivision', 'dimension',
                'minimum', 'maximum']
COLUMN_HEADER = ['resource_name', 'subdivision', 'column_name', 'type',
                 'minimum', 'maximum', 'is_primary_key']


class ConfigTable(object):
    '''
    base class for a table holding informations about resources needed
    by the traffic model, acts like a dictionary

    Parameter
    ---------
    header: list of Strings, the header of the table
    '''
    def __init__(self, header):
        self.header = header
        self.columns = OrderedDict()
        for key in self.header:
            self.columns[key] = []
        self.name = ''

    @property
    def row_count(self):
        '''
        number of rows
        '''
        return len(self.columns[self.header[0]])

    @property
    def column_count(self):
        '''
        number of columns
        '''
        return len(self.columns)

    def __iadd__(self, table):
        '''
        override +=, add rows of another table to this table
        '''
        self.add_table(table)
        return self

    def __repr__(self):
        '''
        String representation of the table
        '''
        col_width = 15

        lines = ['',
                 '----------------',
                 'Table: {}'.format(self.name),
                 '----------------', '']

        table = []
        header = ''
        for col_name in self.columns:
            header += '{0:{width}} |'.format(col_name, width=col_width)
            table.append(self.columns[col_name])
        lines.append(header)
        lines.append(('-' * (col_width + 1) + '|') * self.column_count)

        for row_nr in range(self.row_count):
            row = ''
            for col_nr in range(self.column_count):
                cell = table[col_nr][row_nr]
                if len(str(cell)) > col_width:
                    cell = cell[0:(col_width-3)] + '...'
                row += '{0:{width}} |'.format(cell, width=col_width)
            lines.append(row)

        return '\n'.join(lines)

    def get_rows_by_entries(self, **kwargs):
        '''
        gets the rows inside this table that in whose columns the given
        values are found

        Parameter
        ---------
        kwargs: arguments,
                keys are the names of the columns to be looked in
                values are the values that the column should contain
                e.g. get_rows_by_entries(column_name1 = 'bla',
                                         column_name2 = 'blubb')

        Return
        ------
        table: ConfigTable,
               table containing the rows with the given values in
               the given columns
        '''
        idx = np.ones(self.row_count, dtype=bool)
        for name, value in kwargs.items():
            if not self.columns.has_key(name):
                raise Exception('columns {} does not exist'.format(name))
            idx = idx & (np.array(self[name]) == value)
        ret_table = self[idx]
        return ret_table

    def __getitem__(self, key_or_idx):
        '''
        dictionary-like access to the columns of the table, (dictionary['key'])
        if a boolean array is given, all rows will be returned where True

        Parameter
        ---------
        key_or_idx: String or boolean array,
                    if String, the name of the column
                    if boolean array, the rows that shall be returned

        Return
        ------
        ret: list or ConfigTable,
             if key was given, list of column values is returned
             if boolean array was given, table with wanted rows is returned
        '''
        if key_or_idx.__class__.__name__ == 'ndarray':
            ret = self.__class__()
            for col in self:
                ret[col] = list(np.array(self[col])[key_or_idx])
        else:
            ret = self.columns[key_or_idx]
        return ret

    def __setitem__(self, key, value):
        '''
        dictionary-like access to the columns of the table
        (dictionary['key']=value)
        set the values of the column, if length differs from existing row count
        empty cells will filled with ''

        Parameter
        ---------
        key: String,
            the name of the column
        value: list,
               contains the values that will be set to the column
        '''
        if not self.columns.has_key(key):
            raise Exception('Table has no column {}'.format(key))
        if not isinstance(value, list):
            if self.row_count <= 1:
                value = [value]
            else:
                value = [value for x in range(self.row_count)]
        max_len = 0
        for column in self.columns:
            col_len = len(self.columns[column])
            value_len = len(value)
            if col_len < value_len:
                self.columns[column].extend(['' for x in range(
                    value_len-col_len)])
            col_len = len(self.columns[column])
            if col_len > max_len:
                max_len = col_len
        if len(value) < max_len:
            value.append(['' for x in range(col_len-value_len)])
        self.columns[key] = value

    def __iter__(self):
        '''
        Iterator
        '''
        return self.columns.__iter__()

    def to_csv(self, file_name):
        '''
        write the table to a csv file

        Parameter
        ---------
        file_name: String,
                   the name of the csv file, the table will be written to
        '''
        table = []
        for col_name in self.columns:
            table.append(self.columns[col_name])
        with open(file_name, 'wb') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')
            writer.writerow(self.header)
            for r in xrange(self.row_count):
                row = []
                for c in xrange(self.column_count):
                    row.append(table[c][r])
                writer.writerow(row)

    def from_csv(self, file_name):
        '''
        create a table out of a csv file

        Parameter
        ---------
        file_name: String,
                   the name of the csv file
        '''
        rows = []
        with open(file_name, 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            for row in reader:
                rows.append(row)
        header = rows.pop(0)
        for row in rows:
            table = ConfigTable(header)
            for col_nr in range(len(header)):
                col_name = header[col_nr]
                table[col_name] = row[col_nr]
            self += table

    def add_table(self, table):
        '''
        add the rows of another table to this one, table has to have the
        same columns

        Parameter
        ---------
        table: ConfigTable,
               table containing the rows that will be appended
        '''
        if not isinstance(table, ConfigTable):
            raise Exception('given table has wrong type')
        for column in self:
            if table.columns.has_key(column):
                self[column].extend(table[column])
            else:
                raise Exception('column {} is missing in given table'
                                .format(column))


class InputTable(ConfigTable):
    '''
    a configtable for all input files
    '''
    def __init__(self):
        super(InputTable, self).__init__(INPUT_HEADER)
        self.name = 'Input'


class TableTable(ConfigTable):
    '''
    a configtable for all input tables
    '''
    def __init__(self):
        super(TableTable, self).__init__(TABLE_HEADER)
        self.name = 'Tables'


class ArrayTable(ConfigTable):
    '''
    a configtable for all input arrays
    '''
    def __init__(self):
        super(ArrayTable, self).__init__(ARRAY_HEADER)
        self.name = 'Arrays'


class ColumnTable(ConfigTable):
    '''
    a configtable for all table columns
    '''
    def __init__(self):
        super(ColumnTable, self).__init__(COLUMN_HEADER)
        self.name = 'Columns'


##### parse the input files ####

class ConfigParser(object):
    '''
    base class for parsing a resource file
    '''
    def __init__(self, file_name):
        self.file_name = file_name
        self.input_table = InputTable()

    def parse(self):
        '''
        get file information of the resource file
        '''
        directory, name = os.path.split(self.file_name)
        self.input_table['resource_name'] = name
        self.input_table['type'] = 'unknown'
        return self.input_table


class H5ConfigParser(ConfigParser):
    '''
    parser specifically for HDF5 files and their nodes
    '''
    def __init__(self, file_name):
        super(H5ConfigParser, self).__init__(file_name)
        self.tables = TableTable()
        self.arrays = ArrayTable()
        self.columns = ColumnTable()

    def parse(self):
        '''
        crawl the HDF5 file to find all nodes and columns andget information
        about them

        Return
        ------
        input_table: InputTable,
                     contains one row with the file information
        tables: TableTable,
                contains all tables found in the file and additional
                informations
        arrays: ArrayTable,
                contains all arrays found in the file and additional
                informations
        columns: ColumnTable,
                 contains all columns and additional info
        '''
        directory, fname = os.path.split(self.file_name)
        name = os.path.splitext(fname)[0]
        h5_input = HDF5(self.file_name)
        h5_input.read()
        for table in h5_input.h5_file:
            in_table = InputTable()
            in_table['resource_name'] = name
            in_table['type'] = 'H5{}'.format(table._c_classId.title())
            if table._c_classId == 'TABLE':
                in_table['subdivision'] = table._v_pathname
                t_table = TableTable()
                t_table['resource_name'] = name
                t_table['subdivision'] = table._v_pathname
                t_table['n_rows'] = table.nrows
                self.tables += t_table
                table_data = table.read()
                columns = table_data.dtype
                for col in columns.names:
                    dtype = columns[col]
                    c_table = ColumnTable()
                    c_table['resource_name'] = name
                    c_table['subdivision'] = table._v_pathname
                    c_table['column_name'] = col
                    c_table['type'] = dtype
                    c_table['is_primary_key'] = 0
                    self.columns += c_table
            elif table._c_classId == 'ARRAY':
                in_table['subdivision'] = table._v_pathname
                a_table = ArrayTable()
                a_table['resource_name'] = name
                a_table['subdivision'] = table._v_pathname
                shape = table.shape
                dim = ''
                for d in shape:
                    dim += '{} x '.format(d)
                dim = dim[:-3]
                a_table['dimension'] = dim
                self.arrays += a_table
            else:
                continue
            self.input_table += in_table
        return self.input_table, self.tables, self.arrays, self.columns