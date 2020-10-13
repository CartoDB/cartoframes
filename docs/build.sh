#!/bin/bash

cd ..
pip uninstall cartoframes -y
pip install -e .

cd docs
make clean && make html && make json
