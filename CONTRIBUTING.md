# Contributing to CARTOframes

## Feature request

If you'd like to request a feature, first check <https://github.com/cartodb/cartoframes/issues> to see if your request already exists. If it exists, comment on that issue. If it does not exist, open a new issue clearly defining the need and use case.

## Reporting bugs

If the bug is not already reported, open a new issue. Please give the following information:

* Code snippet that produced the error
* Relevant error messages
* cartoframes version (find it with `print(cartoframes.__version__)`)
* Python version (e.g., 3.5, 2.7, etc.)
* Operation system (Windows, Linux, etc.)

## Pull requests

### External contributors

CARTOframes has automated testing against a working CARTO account, and the authentication information is not public. Because of this, external pull requests currently cannot successfully run the full suite of tests.
 
To run tests, rename the file `secret.json.sample` to `secret.json` and fill in the credentials for a CARTO account to which you have access. NOTE: the tests require access to different CARTO services like the Data Observatory, so the tests consume quota.

To open a pull request:

1. Open against the `develop` branch, which we will keep up-to-date with `master`
2. Tag @andy-esch for review
3. Once the PR has been approved, we'll merge it into `develop`, and then open a fresh pull request against `master` for running the continuous integration. Once tests are successful, we will tag the original contributor there and give final notice before merging in.

### Internal contributors

Open a new pull request against the `master` branch and tag @andy-esch.
