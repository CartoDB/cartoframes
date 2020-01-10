## Installation

This guide is intended for those who are using CARTOframes for the first time and provides the steps to install it **locally**, in a **Jupyter Notebook**, or using a **Virtual Environment**.

### Install CARTOframes using `pip`

CARTOframes can be installed with [`pip`](https://pypi.org/project/pip/) by simply typing one of the following commands to do a system install:

To install the latest beta release (recommended), use the `--pre` flag:

```bash
$ pip install cartoframes --pre
```

To install the latest stable version (soon to be deprecated):

```bash
$ pip install cartoframes
```

To install a specific version, for example, let's say the 1.0rc1 version:

```bash
$ pip install cartoframes==1.0rc1
```


### Install CARTOframes in a Jupyter Notebook

In the CARTOframes Developer Center, all of the examples are in a [Jupyter Notebook](https://jupyter.org/). If you aren't familiar with Jupyter Notebooks, we recommended reading the [beginner documentation](https://jupyter-notebook-beginner-guide.readthedocs.io/en/latest/what_is_jupyter.html) to get familiar with the environment.

To install CARTOframes through a Jupyter Notebook, run this command:

```bash
! pip install cartoframes
```

### Use a Virtual Environment

We recommend installing CARTOframes in a [Virtual Environment](http://docs.python-guide.org/en/latest/dev/virtualenvs/), since they are very useful when working with Python locally. This section provides the necessary information to create a simple Virtual Environment and install CARTOframes inside of it:

```bash
$ virtualenv cartoframes_env
$ source cartoframes_env/bin/activate
(cartoframes_env) $ pip install cartoframes
```

To install a specific version:

```bash
$ virtualenv cartoframes_env
$ source cartoframes_env/bin/activate
(cartoframes_env) $ pip install cartoframes==1.0rc1
```

When the virtual environment is activated, it is visible in the command line prompt, in this case: `(cartoframes_env)`. It can be deactivated by typing `deactivate` to exit the virtualenv:

```bash
(cartoframes_env) $ deactivate
```
