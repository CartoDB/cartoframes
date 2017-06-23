"""
cartoframes
https://github.com/CartoDB/cartoframes
"""

# TODO: update this once carto-python is a module
# NOTE: first do `pip install -r requirements.txt` to get setup

import os
from codecs import open
from setuptools import setup

with open(os.path.join(os.path.abspath(os.path.dirname(__file__)),
                       'README.rst'),
          encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()

setup(
    name='cartoframes',
    version='0.2.2b2',
    description='An experimental Python pandas interface for using CARTO',
    long_description=LONG_DESCRIPTION,
    url='https://github.com/CartoDB/cartoframes',
    author='Andy Eschbacher',
    author_email='andy@carto.com',
    license='BSD',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
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
    packages=['cartoframes'],
    install_requires=['pandas>=0.20.1',
                      'webcolors>=1.7.0',
                      'carto>=1.0.1',
                      'tqdm>=4.14.0',],
    extras_require={
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
            ]},
    package_dir={'cartoframes': 'cartoframes'},
    package_data={
        '': ['LICENSE',
             'CONTRIBUTORS',],
        'cartoframes': ['assets/*',],
    },
)
