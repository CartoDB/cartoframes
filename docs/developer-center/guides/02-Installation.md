## Installation

This guide is intended for those who are going to start using CARTOframes and gives some instructions to install CARTOframes **locally**, in a **Jupyter Notebook** and using a **Virtual Environment**.

### Install CARTOframes using `pip`

It is possible to install CARTOframes with [`pip`](https://pypi.org/project/pip/) by simply typing one of the following commands to do a system install:

To install the latest beta release, use the `--pre` flag:

```bash
$ pip install cartoframes --pre
```

To install the latest stable version:

```bash
$ pip install cartoframes
```

To install a specific version, for example, let's say the 1.0b6 version:

```bash
$ pip install cartoframes==1.0b6
```


### Install CARTOframes in a Jupyter Notebook

In this documentation, all the examples are in a [Jupyter Notebook](https://jupyter.org/). It is recommended to read the [beginner documentation](https://jupyter-notebook-beginner-guide.readthedocs.io/en/latest/what_is_jupyter.html) to get familiar with Jupyter. To install through a Jupyter Notebook, run this command:

```bash
! pip install cartoframes
```

### Use a Virtual Environment

It is recommended to install CARTOframes in a [Virtual Environment](http://docs.python-guide.org/en/latest/dev/virtualenvs/), since they are very useful when working with Python locally. This section provides the necessary information to create a simple Virtual Environment and install CARTOframes in there:

```bash
$ virtualenv cartoframes_env
$ source cartoframes_env/bin/activate
(cartoframes_env) $ pip install cartoframes
```

To install a specific version:

```bash
$ virtualenv cartoframes_env
$ source cartoframes_env/bin/activate
(cartoframes_env) $ pip install cartoframes==1.2.3
```

When the virtual environment is activated, it is visible in the command line prompt, in this case: `(cartoframes_env)`. It can be deactivated by typing `deactivate` to exit the virtualenv:

```bash
(cartoframes_env) $ deactivate
```
