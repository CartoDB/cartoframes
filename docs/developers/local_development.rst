Local Development Setup
=======================

Let's run a local Jupyter Notebook with CARTOFrames, CARTO VL and Airship for local development.

Jupyter Notebook
^^^^^^^^^^^^^^^^

1. Install Python 3

https://www.python.org/downloads/

2. Create virtualenv

.. code::

  python3 -m virtualenv venv

3. Activate virtualenv

.. code::

  source venv/bin/activate

In order to deactivate the virtualenv, run:

.. code::
  
  deactivate

4. Install jupyter

.. code::

  pip install jupyter

5. Install cartoframes package in dev mode

.. code::

  cd cartoframes
  pip install -e .

6. Launch Jupyter notebook

.. code::

  jupyter notebook


CARTO VL
^^^^^^^^

We're going to clone the repository. We can do it in the jupyter-cartoframes directory we've created to set up our local workspace.

.. code::

  git clone git@github.com:CartoDB/carto-vl.git
  cd carto-vl


The local installation of CARTO VL is explained `in this guide <https://github.com/CartoDB/carto-vl/blob/master/DEVELOPERS.md/>`__

Airship
^^^^^^^

Let's clone the Airship repository as well.

.. code::

  git clone git@github.com:CartoDB/airship.git
  cd airship


The local installation of Airship is explained `in this guide <https://github.com/CartoDB/airship/blob/master/DEVELOPERS.md/>`__

CARTOframes JavaScript code
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The JavaScript code is generated using Rollup, a module bundler. In order to save changes in the all the .js files, we need to bundle the code:

Watch changes:

.. code::

  cd cartoframes
  npm run dev

Build:

.. code::

  cd cartoframes
  npm run build


Run all the projects
^^^^^^^^^^^^^^^^^^^^

We've to serve now all the projects as follows:

.. code::

  +---------------------------+---------------------------+
  |/carto-vl                  |/carto-vl                  |
  |$ npm run build:watch      | $ npm run serve           |
  |                           |                           |
  |                           |                           |
  |                           |                           |
  +---------------------------+---------------------------+
  |/airship                   |/airship                   |
  |$ npm run dev              | $ npm run serve           |
  |                           |                           |
  |                           |                           |
  |                           |                           |
  +---------------------------+---------------------------+
  |/cartoframes               |/cartoframes               |
  |(env)$ jupyter notebook    |$ npm run dev              |
  |                           |                           |
  |                           |                           |
  |                           |                           |
  +---------------------------+---------------------------+

Load JavaScript libraries locally
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In order to get Airship and CARTO VL libraries we're serving locally in CARTOFrames, we need to instantiate the map indicating the paths:

.. code:: python

  from cartoframes.auth import set_default_credentials
  from cartoframes.viz import Map, Layer

  set_default_credentials('cartoframes')

  Map(
      Layer('dataset_name'),
      _carto_vl_path='http://localhost:8080',
      _airship_path='http://localhost:5000'
  )

We've a lot of public datasets in both `cartoframes` and `cartovl` accounts that we use for the examples, but I've you've a personal CARTO account you can use your credentials.

Reload changes
^^^^^^^^^^^^^^

When making changes in CARTOFrames library, in the notebook, click on kernel > Restart and Run all. When making changes in CARTO VL or Airship, click on run (the page doesn't need to be reloaded)
