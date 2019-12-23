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

- developer-center: Guides and examples extructure to be published in the developer center
- developers: Internal documentation
- guides: Old guides. These guides will be moved to the new ones and deleted eventually
- includes: Contains the different doc sections, which are included in `cartoframes.rst` file

Structure
~~~~~~~~~

`cartoframes.rst` file is the main entry point for the rest of the documentation.
We generate a single document file from this one to build the result documentation.
In the `includes` directory we place the different sections, that are included from `cartoframes.rst`.

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

- If you want to add a new section, create a file with the name of this section in `docs/includes`, and include it in `docs/cartoframes.rst`.
- Use `automodule` syntax to include module content:

.. code::
    .. automodule:: cartoframes.module.other_module
    :members:

- Include the file you want to import in the `__init__.py` file properly

Developer center
----------------

Guides, Examples and Support pages are generated in the developer center from a specific documentation branch.
Each release has a `docs/v.M.m.p` reference branch, that is generated at the same time the release tag is created. The difference is that
we have separated branches in order to be able to change the docs after the release.

Writing Documentation
~~~~~~~~~~~~~~~~~~~~~

Documentation is placed in `/docs/developer-center` directory.

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

Guides
------

Guides are placed in the `/docs/developer-center/guides` directory. They're written using markdown format.
There's a `guide-boilerplate<./guide-boilerplate.md>`_. that can be used as a starting point.

Examples
--------

Examples are placed in the `/examples` directory. These examples are Jupyter Notebooks, that are converted to `html` to be rendered in the developer center.
The `examples.json` file placed in `/docs/developer-center/examples` is used to select and organize the examples to expose in the developer center.
When adding a new notebook, if it needs to be published in the developer center, it must be included in this config file.


Errors and Exceptions
~~~~~~~~~~~~~~~~~~~~~

- `Exception`: general exception.

Built-in
--------

- `AttributeError`: raised on the attribute assignment or reference fails: `c.wrong`
- `IndexError`: raised when the index of a sequence is out of range: `l[n+1]`
- `KeyError`: raised when a key is not found in a dictionary: `d['wrong']`
- `TypeError`: raised when a function or operation is applied to an object of an incorrect type: `'2'+2`
- `ValueError`: raised when a function gets an argument of correct type but improper value: `int('xyz')`

Custom
------