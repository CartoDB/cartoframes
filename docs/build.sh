#!/bin/bash

rm setup.rst
rm modules.rst
rm cartoframes*
rm test*

cd ..
pip uninstall cartoframes -y
pip install .
sphinx-apidoc -o docs .

cd docs
make clean && make html && make json
