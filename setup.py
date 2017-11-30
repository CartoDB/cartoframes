#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import io
from codecs import open
from setuptools import setup

NAME = 'cartoframes'
DESCRIPTION = 'An experimental Python pandas interface for using CARTO'
URL = 'https://github.com/CartoDB/cartoframes'
AUTHOR = 'Andy Eschbacher'
EMAIL = 'andy@carto.com'

REQUIRES = [
    'pandas>=0.20.1',
    'webcolors>=1.7.0',
    'carto>=1.1.0',
    'tqdm>=4.14.0,!=4.18.0',
    'appdirs>=1.4.3',
]

EXTRAS_REQUIRE = {
    ':python_version == "2.7"': [
        'IPython>=5.0.0,<6.0.0',
        ],
    ':python_version == "3.4"': [
        'IPython>=6.0.0'
        ],
    ':python_version == "3.5"': [
        'IPython>=6.0.0'
        ],
    ':python_version == "3.6"': [
        'IPython>=6.0.0'
        ],
}

here = os.path.abspath(os.path.dirname(__file__))

with io.open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = '\n' + f.read()

about = {}
with open(os.path.join(here, NAME, '__version__.py')) as f:
        exec(f.read(), about)

setup(
    name=NAME,
    version=about['__version__'],
    description=DESCRIPTION,
    long_description=long_description,
    url=URL,
    author=AUTHOR,
    author_email=EMAIL,
    license='BSD',
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
        'Programming Language :: Python :: 3.6'
    ],
    keywords='carto data science maps spatial pandas',
    packages=[
        'cartoframes',
        ],
    install_requires=REQUIRES,
    extras_require=EXTRAS_REQUIRE,
    include_package_data=True,
    package_dir={'cartoframes': 'cartoframes'},
    package_data={
        '': [
            'LICENSE',
            'CONTRIBUTORS',
            ],
        'cartoframes': [
            'assets/*',
            ],
    },
)
