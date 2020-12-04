Documentation
=============

Reference
---------

We're using Sphinx to automatically generate documentation. We need to install the following libraries:

Requirements
~~~~~~~~~~~~

- sphinx>=1.6.5
- sphinxcontrib-napoleon>=0.7.0

This can be installed with the following command:

.. code::
    $ pip install -r docs/requirements.txt

The docs directory
~~~~~~~~~~~~~~~~~~

The docs directory contains:

- developers: Internal documentation.
- examples: Contains the examples (notebooks) for the Developer Center.
- guides: Contains the guides (notebooks) for the Developer Center.
- reference: Contains the rst index documents to generate the reference for the Developer Center.
- support: Contains the support files for the Developer Center.

Structure
~~~~~~~~~

`cartoframes.rst` file is the main entry point for the rest of the documentation.
We generate a single document file from this one to build the result documentation.
In the `reference` directory we place the different sections, that are included from `cartoframes.rst`.

Generating docs locally
~~~~~~~~~~~~~~~~~~~~~~~

From the `docs` directory: 

It's needed to have `cartoframes` installed locally. It's possible to do so by just running the following script:

.. code::
   ./build.sh


In order to build the documentation using `sphinx-build <https://www.sphinx-doc.org/en/master/man/sphinx-build.html/>`__ :

.. code:: 
    make <format>

In order to test the output locally in your browser, we can generate the html:

.. code:: 
    make html


The output will be in `build/html` directory.

Adding documentation
~~~~~~~~~~~~~~~~~~~~

Add documentation to the API reference:

- If you want to add a new section, create a file with the name of this section in `docs/reference`, and include it in `docs/cartoframes.rst`.
- Use `automodule` syntax to include module content:

.. code::
    .. automodule:: cartoframes.module.other_module
    :members:

- Use `autoclass` syntax to include class content:

.. code::
    .. autoclass:: cartoframes.module.MyClass
    :members:

- Include the file you want to import in the `__init__.py` file properly

Developer center
----------------

Guides, Examples and Support pages are generated in the developer center from a specific documentation branch.
Each release has a `docs/v.M.m.p` reference branch, that is generated at the same time the release tag is created. The difference is that
we have separated branches in order to be able to change the docs after the release.

Writing Documentation
~~~~~~~~~~~~~~~~~~~~~

Documentation is placed in `/docs` directory.

- In order to test it in the developer center, it's necessary to change the branch to be tested in the `config.js` (instructions are explained in the developer center repository)
- In order to modify the documentation of a specific version, just:
    
Download the docs branch and create from it a new one:

    Note: Don't create the branch starting with `docs/*`, because this namespace is used only when creating a documentation-featured branch from a version


.. code::
    $ git fetch origin docs/v.M.m.p
    $ git checkout docs/v.M.m.p
    $ git checkout -b your-fix-description

Apply the necessary changes:

    Note: If you're changing the examples and want to test them locally, don't forget to use the cartoframes version you've to use for the examples.

.. code::
    $ git add .
    $ git commit -m "Commit description"
    $ git push origin your-fix-description

And, finally, open a Pull Request against the docs branch.

    Note: Don't forget to add a reviewer

After that, in order to see the changes applied in the developer center, deploy the production version through Jenkins.

Errors and Exceptions
~~~~~~~~~~~~~~~~~~~~~

- `Exception`: general exception.

Built-in
--------

- `AttributeError`: raised on the attribute assignment or reference fails: `c.wrong`
- `IndexError`: raised when the index of a sequence is out of range: `l[n+1]`
- `KeyError`: raised when a key is not found in a dictionary: `d['wrong']`
- `OSError`: raised when a system function returns a system-related error, including I/O failures such as "file not found" or "disk full".
- `TypeError`: raised when a function or operation is applied to an object of an incorrect type: `'2'+2`
- `ValueError`: raised when a function gets an argument of correct type but improper value: `int('xyz')`

Custom
------

- DOError.
    - CatalogError.
    - EnrichmentError.
- PublishError.


Development with Staging
~~~~~~~~~~~~~~~~~~~~~~~~

Before releasing to production we need to test everything in staging. In order to do that, we need to configure CARTOframes to point to staging.
There is a set of internal functions to configure the default DO credentials used by the DO Catalog.

.. code::
    from cartoframes.auth import set_default_credentials

    set_default_credentials('https://USER.carto-staging.com', 'API_KEY')

.. code::
    from cartoframes.auth.defaults import set_default_do_credentials

    set_default_do_credentials(username='USER', base_url='https://ORG.carto-staging.com')

    # After that, every request to the DO Catalog will be done with the provided credentials
    # instead of the default ones for production (user 'do-metadata').


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
