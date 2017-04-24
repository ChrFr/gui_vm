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

    with tables.open_file(h5_in_path) as h5_in:

        try:
            for name, mode_table in modes.items():
                path = mode_path + '/' + mode_table
                table = h5_in.get_node(path).read()
                mode_sum = table.sum()
                meta['Wegesumme ' + name] = int(round(mode_sum))
                modes[name] = mode_sum
                modes_sum += mode_sum
        except tables.NoSuchNodeError as e:
            print e.message
            meta = {'Fehler': 'Benötigte Tabelle fehlt: "{}"'.format(
                e.message
            )}
        else:
            meta['Summe aller Wege'] = int(round(modes_sum))
            for name, mode_sum in modes.items():
                meta['Anteil ' + name] = '{:.2%}'.format(mode_sum / modes_sum)

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
                        dest="csv_out_path")

    arguments = parser.parse_args()

    h5_in_path = arguments.h5_in_path
    csv_out_path = arguments.csv_out_path
    if h5_in_path is None:
        print('Input-Datei muss angegeben werden.')
    else:
        if csv_out_path is None:
            csv_out_path = h5_in_path.replace('.h5', '.csv')
        evaluate(h5_in_path, csv_out_path)

if __name__ == "__main__":
    startmain()