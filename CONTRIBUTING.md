# Contributing to CARTOframes

The CARTO platform is an open-source ecosystem. Read the [fundamentals of the CARTO](https://carto.com/developers/fundamentals/components/) to learn about its architecture and components. We are more than happy to receive your contributions to the code and the documentation as well.

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

## Completing documentation

CARTOframes documentation is located inline in the functions, classes, and methods in the code. There is additional documentation, guides, and examples in the ```docs/``` folder. That folder is the content that appears in the [Developer Center](http://carto.com/developers/cartoframes/). Just follow the instructions described in [contributing code](#pull-requests) and after accepting your pull request, we will make it appear online :).

**Tip:** A convenient, easy way of proposing changes in documentation is by using the GitHub editor directly on the web. You can easily create a branch with your changes and make a PR from there.

## Submitting contributions

You will need to sign a Contributor License Agreement (CLA) before making a submission. [Learn more here](https://carto.com/contributions).
