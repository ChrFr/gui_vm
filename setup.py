# -*- coding: utf-8 -*-
#
from setuptools import setup, find_packages

setup(
    name="gui_vm",
    version="1.01b",
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
    packages=find_packages('src', exclude=['default', 'icons', 'ez_setup']),
    namespace_packages=['gui_vm'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    package_data={
        'gui_vm': ['model/maxem/Maxem.xml',
                   'config_template.xml'],
    },

    # deactivated requirements to avoid vcvarsall.bat errors in wheel installer, have to be installed with conda/pip before
    install_requires=[
        'setuptools'#,
        #'numpy',
        #'tables',
        #'lxml'
    ],

    # PyQT 4 needed, no disutils available for the package.
    # install it seperately

    entry_points={
        'console_scripts': [
            'gui_vm=gui_vm.main:startmain',
            #'gui_vm.clone_scenario=gui_vm.clone_scenario:main',
            'get_param_from_config=gui_vm.get_param_from_config:main'
        ],
    },
)
