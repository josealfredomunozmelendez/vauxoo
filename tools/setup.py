#! /usr/bin/env python
# -*- coding: utf-8 *-
from setuptools import setup

setup(
    name='vxmigration',
    version='1.0.1',
    py_modules=['import_data'],
    install_requires=[
        'Click',
        'OdooRPC',
        'Py',
        'simplejson',
        'psycopg2',
        'click-log',
    ],
    entry_points='''
        [console_scripts]
        vxmigration=import_data:main
    '''
)
