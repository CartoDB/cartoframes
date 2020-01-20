# Contributing to CARTOframes

The CARTO platform is an open-source ecosystem. Read the [fundamentals of the CARTO](https://carto.com/developers/fundamentals/components/) to learn about its architecture and components. We are more than happy to receive your contributions to the code and the documentation as well.

## Feature request

If you'd like to request a feature, first check <https://github.com/cartodb/cartoframes/issues> to see if your request already exists. If it exists, comment on that issue. If it does not exist, open a new issue clearly defining the need and use case.

## Reporting bugs

If the bug is not already reported, open a new issue. Please give the following information:

* Code snippet that produced the error
* Relevant error messages
* cartoframes version (find it with `print(cartoframes.__version__)`)
* Python version (e.g., 3.5, etc.)
* Operation system (Windows, Linux, etc.)

## Pull requests

### External contributors

CARTOframes has automated testing against a working CARTO account, and the authentication information is not public. Because of this, external pull requests currently cannot successfully run the full suite of tests.

To run tests, rename the file `secret.json.sample` to `secret.json` and fill in the credentials for a CARTO account to which you have access. NOTE: the tests require access to different CARTO services like the Data Observatory, so the tests consume quota.

To open a pull request:

1. Open against the `develop` branch, which we will keep up-to-date with `master`
2. Once the PR has been approved, we'll merge it into `develop`, and then open a fresh pull request against `master` for running the continuous integration. Once tests are successful, we will tag the original contributor there and give final notice before merging in.

### `carto-python` dependency

CARTOframes uses [carto-python](https://github.com/CartoDB/carto-python) intensively. It has the clients to connect to the different CARTO APIs. Usually, when we are developing in CARTOframes, we add the following line in the `requirements.txt` file to work with the last code in the master branch:

```
-e git+https://github.com/CartoDB/carto-python.git#egg=carto
```

Of course, it should be removed before a release is done.

### Internal contributors

Open a new pull request against the `develop` branch.

## Completing documentation

CARTOframes documentation is located inline in the functions, classes, and methods in the code. There is additional documentation, guides, and examples in the ```docs/``` folder. That folder is the content that appears in the [Developer Center](http://carto.com/developers/cartoframes/). Just follow the instructions described in [contributing code](#pull-requests) and after accepting your pull request, we will make it appear online :).

**Tip:** A convenient, easy way of proposing changes in documentation is by using the GitHub editor directly on the web. You can easily create a branch with your changes and make a PR from there.

## Releases

To release a new version of CARTOframes, create a new branch off of `master` called `vX.Y.Z_release`, where `X.Y.Z` should be replaced with the specific version to be released (e.g., 0.10.1). After this branch is created, update the following files:

1. ``cartoframes/__version__.py`` should have the newest version number in the ``__version__`` variable
2. NEWS.rst should be updated with all of the changes happening in this version. It should include the release number and the date of the release. Looking at merged pull requests sorted by last updated is a good way to ensure features are not missed.
3. The README.rst should be updated so that the mybinder tag at the top of the file is the release number/tag

Ensure that documentation is building correctly by building this branch in readthedocs. If not, this is a good time to fix documentation before publishing. You needed to be added as a contributor on readthedocs to be able to configure builds.

After the tests pass, merge into master. Next, we publish a release to [PyPi](https://pypi.org/project/cartoframes/) and [GitHub](https://github.com/CartoDB/cartoframes/releases).

### Documentation (readthedocs)

This step needs to be completed before any releases, but it is here as a reminder that documentation should not be ignored. Docs are built with [ReadTheDocs](https://cartoframes.readthedocs.io/en/stable/) automatically from any tagged release and a few select branches. ``master`` is the docs build for ``latest``. Once docs are working from master from the previous step, ensure that the version shows up in the default docs page: https://cartoframes.readthedocs.io/en/stable/

### PyPi release

Run `make publish` in the base cartoframes directory. For a new release to be published on PyPi you need to be added as an author on the [PyPi's cartoframes project](https://pypi.org/project/cartoframes/). Also make sure that [`twine`](https://pypi.org/project/twine/) is installed.


### GitHub release

1. Make sure `master` is fresh from the `vX.Y.Z_release` merge
2. Title release `vX.Y.Z Release`
3. Add latest entry from NEWS.rst
4. Add the dist files from `make dist` (``cartoframes-X.Y.Z-py2-py3-none-any.whl`` and ``cartoframes-X.Y.Z.tar.gz``)
5. Select pre-release (for now)

## Submitting contributions

You will need to sign a Contributor License Agreement (CLA) before making a submission. [Learn more here](https://carto.com/contributions).
