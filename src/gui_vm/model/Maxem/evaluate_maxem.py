# -*- coding: utf-8 -*-
import tables
from argparse import ArgumentParser
from collections import OrderedDict
import os
import csv

def evaluate(h5_in_path, csv_out):
    
    mode_path = '/modes'
    modes = OrderedDict({
        'Fahrrad': 'bicycle',
        'Auto': 'car',
        'zu Fuß': 'foot',
        'Pkw-Mitfahrer': 'passenger',
        'ÖPNV': 'put'
    })
    meta = OrderedDict()
    modes_sum = 0
    
    if h5_in_path is None or not os.path.exists(h5_in_path):
        print 'Datei {} nicht vorhanden!'.format(h5_in_path)
        return
    h5_in = tables.openFile(h5_in_path)
    
    for name, mode_table in modes.items():
        table = h5_in.getNode(mode_path + '/' + mode_table).read()
        mode_sum = table.sum()
        meta['Wegesumme ' + name] = int(round(mode_sum))
        modes[name] = mode_sum
        modes_sum += mode_sum
    meta['Summe aller Wege'] = int(round(modes_sum))
    for name, mode_sum in modes.items():
        meta['Anteil ' + name] = '{:.2%}'.format(mode_sum / modes_sum)
        
    h5_in.close()   
    
    with open(csv_out, 'wb') as csv_file:
        w = csv.DictWriter(csv_file, meta.keys())
        w.writeheader()
        w.writerow(meta)

def startmain():
    parser = ArgumentParser(description="Maxem")

    parser.add_argument("-i", action="store",
                        help="Maxem demand file",
                        dest="h5_in_path")

    parser.add_argument("-o", action="store",
                        help="csv output file",
                        dest="csv_out_path", default='maxem_out.csv')

    arguments = parser.parse_args()

    if arguments.h5_in_path is None:
        print('Input-Datei muss angegeben werden.')
    else:
        evaluate(arguments.h5_in_path, arguments.csv_out_path)
    
if __name__ == "__main__":
    startmain()