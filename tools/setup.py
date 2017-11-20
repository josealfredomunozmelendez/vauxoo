#! /usr/bin/env python
# -*- coding: utf-8 *-
from setuptools import setup

def read_requirements():
    with open('requirements.txt', 'r') as reqfile:
        data = reqfile.read().splitlines()
    return data

setup(
    name='vxmigration',
    version='1.0.1',
    py_modules=['import_data'],
    install_requires=read_requirements(),
    entry_points='''
        [console_scripts]
        vxmigration=import_data:main
    '''
)
