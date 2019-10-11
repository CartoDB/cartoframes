#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import io
from codecs import open
from setuptools import setup, find_packages


def walk_subpkg(name):
    data_files = []
    package_dir = 'cartoframes'
    for parent, dirs, files in os.walk(os.path.join(package_dir, name)):
        # Remove package_dir from the path.
        sub_dir = os.sep.join(parent.split(os.sep)[1:])
        for f in files:
            data_files.append(os.path.join(sub_dir, f))
    return data_files


REQUIRES = [
    'appdirs>=1.4.3,<2.0',
    'carto>=1.7.0,<2.0',
    'jinja2>=2.10.1,<3.0',
    'geopandas>=0.6.0,<1.0',
    'tqdm>=4.32.1,<5.0',
    'unidecode>=1.1.0,<2.0',
    'pyarrow>=0.14.1,<1.0',
    'google-cloud-bigquery>=1.19.0,<2.0',
    'geojson>=2.5.0,<3.0'
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

here = os.path.abspath(os.path.dirname(__file__))

with io.open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = '\n' + f.read()

about = {}
with open(os.path.join(here, 'cartoframes', '__version__.py'), 'r', 'utf-8') as f:
    exec(f.read(), about)

setup(
    name=about['__title__'],
    version=about['__version__'],
    description=about['__description__'],
    long_description=long_description,
    url=about['__url__'],
    author=about['__author__'],
    author_email=about['__email__'],
    license=about['__license__'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],
    keywords='carto data science maps spatial pandas',
    packages=find_packages(),
    install_requires=REQUIRES,
    python_requires=">=2.6, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
    include_package_data=True,
    package_dir={'cartoframes': 'cartoframes'},
    package_data=PACKAGE_DATA,
)
