##### backend for physically storing data #####
import tables
import os


class HDF5(object):
    """
    Backend to access HDF5 files
    """
    def __init__(self, filename):
        self.filename = filename
        self.h5_file = None

    def __del__(self):
        if self.h5_file is not None:
            self.h5_file.close()

    @property
    def file_exists(self):
        return os.path.isfile(self.filename)

    def read(self):
        if self.file_exists:
            try:
                self.h5_file = tables.openFile(self.filename, 'r')
            except:
                return False
            return True
        else:
            return False

    def get_table(self, table_path):
        if self.h5_file is not None:
            try:
                table = self.h5_file.getNode(table_path)
                return table
            except tables.NoSuchNodeError:
                return None
        return None


def equal_dtypes(self):
    pass