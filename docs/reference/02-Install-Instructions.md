## Install Instructions


To install cartoframes on your machine, do the following to install the latest version:

```bash
$ pip install cartoframes
```

CARTOFrames is continuously tested on Python versions 2.7, 3.5, and 3.6. It is recommended to use cartoframes in Jupyter Notebooks (pip install jupyter). See the example usage section below or notebooks in the [examples directory](https://github.com/CartoDB/cartoframes/tree/master/examples) for using cartoframes in that environment.

### Virtual Environment

#### Using virtualenv

Make sure your virtualenv package is installed and up-to-date. See the [official Python packaging page](https://packaging.python.org/guides/installing-using-pip-and-virtualenv/) for more information.

To setup cartoframes and Jupyter in a [virtual environment](http://python-guide.readthedocs.io/en/latest/dev/virtualenvs/):

```bash
$ virtualenv venv
$ source venv/bin/activate
(venv) $ pip install cartoframes jupyter
(venv) $ jupyter notebook
```

Then create a new notebook and try the example code snippets below with tables that are in your CARTO account.

#### Using pipenv

Alternatively, [pipenv](https://pipenv.readthedocs.io/en/latest/) provides an easy way to manage virtual environments. The steps below are:

1.  Create a virtual environment with Python 3.4+ (recommended instead of Python 2.7)
2.  Install cartoframes and Jupyter (optional) into the virtual environment
3.  Enter the virtual environment
4.  Launch a Jupyter notebook server

```bash
$ pipenv --three
$ pipenv install cartoframes jupyter
$ pipenv shell
```

Next, run a Python kernel by typing $ python, $ jupyter notebook, or however you typically run Python.

### Native pip

If you install packages at a system level, you can install cartoframes with:

```python
$ pip install cartoframes
```
