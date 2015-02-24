# -*- coding: utf-8 -*-
#
from distutils.core import setup
import py2exe, numpy

py2exe_options = {
    #'excludes' : ['_ssl',  # Exclude _ssl
              #'pyreadline', 'difflib', 'doctest',
              #'optparse', 'pickle', 'calendar',
              #'default', 'icons', 'ez_setup'],  # Exclude standard library
    #dll_excludes=['msvcr71.dll'],  # Exclude msvcr71
    'compressed' : True,  # Compress library.zip
    'includes' : ['sip',
                'numpy',
                'tables',
                'numexpr',
                'numexpr.__config__',
                'lxml._elementpath'
                ]
}

setup(
    name="gui_vm",
    version="0.5",
    url='https://github.com/ChrFr/gui_vm',
    author='Christoph Franke',
    description="graphical user interface for different traffic models",
    classifiers=[
        "Programming Language :: Python",
        "Intended Audience :: Traffic Planners",
        "License :: Other/Proprietary License",
        "Natural Language :: German",
        "Operating System :: Windows",
        "Programming Language :: Python",
    ],
    keywords='GUI_VM',
    download_url='',
    license='other',
    #packages=find_packages('src', exclude=['default', 'icons', 'ez_setup']),
    namespace_packages=['gui_vm'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    windows=[{"script":"src/gui_vm/main.py",
              "icon_resources": [(1, "src/gui_vm/favicon.ico")]}],
    options={'py2exe': py2exe_options},
    data_files=['src/gui_vm/default_config.xml',
                'src/gui_vm/Maxem_columns.csv',
                'src/gui_vm/Maxem_arrays.csv',
                'src/gui_vm/Maxem_input.csv',
                'src/gui_vm/Maxem_tables.csv',
                'src/gui_vm/maxem.py',
                'src/gui_vm/evaluate_maxem.py'
                ]
)
