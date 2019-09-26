Documentation
=============

We're using Sphinx to automatically generate documentation. We need to install the following libraries:

Requirements
------------

- sphinx>=1.6.5
- sphinxcontrib-napoleon>=0.7.0
- geopandas>=0.5.1

This can be installed with the following command:

.. code::
    $ pip install -r docs/requirements.txt

The docs directory
------------------

The docs directory contains:

- developer-center: Guides, support and examples documentation to be published in the developer center
- developers: Internal documentation
- guides: Old guides. These guides will be moved to the new ones and deleted eventually
- includes: Contains the different doc sections, which are included in `cartoframes.rst` file

Structure
---------

`cartoframes.rst` file is the main entry point for the rest of the documentation.
We generate a single document file from this one to build the result documentation.
In the `includes` directory we place the different sections, that are included from `cartoframes.rst`.

Generating docs locally
-----------------------

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
--------------------

Add documentation to the API reference:

- If you want to add a new section, create a file with the name of this section in `docs/includes`, and include it in `docs/cartoframes.rst`.
- Use `automodule` syntax to include module content:

.. code::
    .. automodule:: cartoframes.module.other_module
    :members:

- Include the file you want to import in the `__init__.py` file properly
