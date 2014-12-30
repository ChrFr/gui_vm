# -*- coding: utf-8 -*-
import tables
import os
import sys
import ctypes
import platform

def hard_copy(src_filename, dest_filename,
              callback=None, block_size=512):
    '''
    copy file blockwise to given destination

    Parameter
    ---------
    src_filename: String,
                  name of the file to copy (incl. path)
    dest_filename: String,
                   name of the file where the content of the file will be
                   copied into (incl. path)
    block_size: int, optional
                size of the copied blocks
    callback: function, optional
              a method tracking the progress from 0 to 100

    Return
    ------
    successful: bool, True if copying was successful
    '''

    src = open(src_filename, "rb")
    #you can't copy a file into itself
    if os.path.normpath(src_filename) == os.path.normpath(dest_filename):
        return False, 'Quelle und Ziel sind identisch!'
    dest_dir, dest_fn = os.path.split(dest_filename)
    src_size = os.stat(src_filename).st_size
    free = get_free_space(dest_dir)
    if src_size >= free:
        return (False,
                'Nicht genug Speicherplatz in {} vorhanden!'.format(dest_dir))
    #create directory, if not exists
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    dest = open(dest_filename, "wb")
    callback(0)
    cur_block_pos = 0

    while True:
        cur_block = src.read(block_size)
        cur_block_pos += block_size
        #track progress (in percentage of 100)
        progress = (float(cur_block_pos) / float(src_size) * 100)
        callback(progress)

        #end of file
        if not cur_block:
            sys.stderr.write('\n')
            break
        else:
            dest.write(cur_block)

    src.close()
    dest.close()

    #check if destination file has same file size as input file
    dest_size = os.stat(dest_filename).st_size
    if dest_size != src_size:
        return False, 'Datei wurde nicht vollständig kopiert!'

    else:
        return True, 'Datei erfolgreich kopiert.'

def get_free_space(folder):
    """
    Return folder/drive free space (in bytes)
    """
    if platform.system() == 'Windows':
        free_bytes = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(folder),
                                                   None, None,
                                                   ctypes.pointer(free_bytes))
        return free_bytes.value
    else:
        st = os.statvfs(folder)
        return st.f_bavail * st.f_frsize

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


