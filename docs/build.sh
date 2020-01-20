#!/bin/bash

cd ..
pip uninstall cartoframes -y
pip install .

cd docs
make clean && make html && make json
