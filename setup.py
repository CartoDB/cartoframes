"""
cartoframes

NOTE: to install with pip in edit mode, use
  `pip --process-dependency-links --upgrade -e .`
"""

# TODO: update this once carto-python is a module
# NOTE: first do `pip install -r requirements.txt` to get setup

from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='cartoframes',
    version='0.1.2',
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
    install_requires=['pandas'],
    package_data={
        '': ['LICENSE', 'CONTRIBUTORS'],
    },
)
