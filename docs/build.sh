#!/bin/bash

cd ..
pip uninstall cartoframes -y
pip install .

cd docs
sphinx-apidoc -o . ..
make clean && make html && make json
