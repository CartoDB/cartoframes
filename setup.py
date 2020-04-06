#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages


def walk_subpkg(name):
    data_files = []
    package_dir = 'cartoframes'
    for parent, _, files in os.walk(os.path.join(package_dir, name)):
        # Remove package_dir from the path.
        sub_dir = os.sep.join(parent.split(os.sep)[1:])
        for _file in files:
            data_files.append(os.path.join(sub_dir, _file))
    return data_files


def get_version():
    _version = {}
    with open('cartoframes/_version.py') as fp:
        exec(fp.read(), _version)
    return _version['__version__']


REQUIRES = [
    'appdirs>=1.4.3,<2.0',
    'carto>=1.10.1,<2.0',
    'jinja2>=2.10.1,<3.0',
    'geopandas>=0.6.0,<1.0',
    'tqdm>=4.32.1,<5.0',
    'unidecode>=1.1.0,<2.0',
    'google-cloud-storage==1.23.0',
    'google-cloud-bigquery==1.22.0',
    'google-cloud-bigquery-storage==0.7.0',
    'fastavro==0.22.7',
    'semantic_version>=2.8.0,<3'
]


EXTRAS_REQUIRES_TESTS = [
    'pytest',
    'pytest-mock',
    'pylint',
    'flake8'
]


PACKAGE_DATA = {
    '': [
        'LICENSE',
        'CONTRIBUTORS',
    ],
    'cartoframes': [
        'assets/*',
        'assets/*.j2'
    ] + walk_subpkg('assets'),
}


DISTNAME = 'cartoframes'
DESCRIPTION = 'CARTO Python package for data scientists'
LICENSE = 'BSD'
URL = 'https://github.com/CartoDB/cartoframes'
AUTHOR = 'CARTO'
EMAIL = 'contact@carto.com'


setup(
    name=DISTNAME,
    version=get_version(),

    description=DESCRIPTION,
    long_description=open('README.rst').read(),
    long_description_content_type='text/x-rst',
    license=LICENSE,
    url=URL,

    author=AUTHOR,
    author_email=EMAIL,

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8'
    ],
    keywords=['carto', 'data', 'science', 'maps', 'spatial', 'pandas'],

    packages=find_packages(),
    package_data=PACKAGE_DATA,
    package_dir={'cartoframes': 'cartoframes'},
    include_package_data=True,

    install_requires=REQUIRES,
    extras_requires={
        'tests': EXTRAS_REQUIRES_TESTS
    },
    python_requires='>=3.5'
)
