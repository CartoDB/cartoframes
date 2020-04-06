***********
CARTOframes
***********

.. image:: https://travis-ci.org/CartoDB/cartoframes.svg?branch=develop
    :target: https://travis-ci.org/CartoDB/cartoframes
.. image:: https://img.shields.io/badge/pypi-v1.0.2-orange
    :target: https://pypi.org/project/cartoframes/1.0.2

A Python package for integrating `CARTO <https://carto.com/>`__ maps, analysis, and data services into data science workflows.

Python data analysis workflows often rely on the de facto standards `pandas <http://pandas.pydata.org/>`__ and `Jupyter notebooks <http://jupyter.org/>`__. Integrating CARTO into this workflow saves data scientists time and energy by not having to export datasets as files or retain multiple copies of the data. Instead, CARTOframes give the ability to communicate reproducible analysis while providing the ability to gain from CARTO's services like hosted, dynamic or static maps and `Data Observatory <https://carto.com/platform/location-data-streams/>`__ augmentation.

Try it Out
==========

* Stable (1.0.2): |stable|
* Latest (develop branch): |develop|

.. |stable| image:: https://mybinder.org/badge_logo.svg
    :target: https://mybinder.org/v2/gh/cartodb/cartoframes/v1.0.2?filepath=examples

.. |develop| image:: https://mybinder.org/badge_logo.svg
    :target: https://mybinder.org/v2/gh/cartodb/cartoframes/develop?filepath=examples

If you do not have an API key, you can still use cartoframes for creating maps locally.

    The example context only provides read access, so not all cartoframes features are available. For full access, `Start a free trial <https://carto.com/signup>`__ or get free access with a `GitHub Student Developer Pack <https://education.github.com/pack>`__.

Features
========

- Create interactive maps from pandas DataFrames (CARTO account not required)
- Publish interactive maps to CARTO's platform
- Write and read pandas DataFrames to/from CARTO tables and queries
- Create customizable, interactive CARTO maps in a Jupyter notebook using DataFrames or hosted data
- Augment your data with CARTO's Data Observatory
- Use CARTO for cloud-based analysis

Common Uses
===========

- Visualize spatial data programmatically as matplotlib images, as notebook-embedded interactive maps, or published map visualizations
- Perform cloud-based spatial data processing using CARTO's analysis tools
- Extract, transform, and Load (ETL) data using the Python ecosystem for getting data into and out of CARTO
- Data Services integrations using CARTO's `Location Data Streams <https://carto.com/platform/location-data-streams/>`__

More info
=========

- Complete documentation: https://carto.com/developers/cartoframes/
- Source code: https://github.com/CartoDB/cartoframes
- Bug tracker / feature requests: https://github.com/CartoDB/cartoframes/issues

    `cartoframes` users must have a CARTO API key for most `cartoframes` functionality. For example, writing DataFrames to an account, reading from private tables, and visualizing data on maps all require an API key. CARTO provides API keys for education and nonprofit uses, among others. Request access at support@carto.com. API key access is also given through `GitHub's Student Developer Pack <https://carto.com/blog/carto-is-part-of-the-github-student-pack>`__.
