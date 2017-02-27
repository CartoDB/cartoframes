"""
cartoframes
"""

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
# TODO: fill this in
packages = [
    'pandas',
]


with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='cartoframes',
    version='0.0.1',
    description='An experimental Python pandas interface for using CARTO',
    long_description=long_description,
    url='https://github.com/CartoDB/cartoframes',
    author='Andy Eschbacher',
    author_email='andy@carto.com',
    license='BSD',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],
    keywords='data science maps spatial pandas',
    packages=['cartoframes'],

    install_requires=[
        'carto',
        'pandas'
    ],
    dependency_links = [        'git+https://github.com/CartoDB/carto-python.git@e404d9a96afcd5cdd72cadf8e5461c3e67fd6d76#egg=carto'],


    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    # extras_require={
    #     'dev': ['check-manifest'],
    #     'test': ['coverage'],
    # },

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    package_data={
        '': ['LICENSE'],
    },
)
