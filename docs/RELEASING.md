# Releasing

We follow the git-flow model to generate the releases. The version numbers are M.m.u:

- M: major
- m: minor
- u: micro
- p: patch (only for hotfixes)

## The release branch

To freeze the changes and start the release process, we create a release branch from `develop`.

```
git checkout develop
git checkout -b release/M.m.u
```

In that branch, we bump the version number and update some files:

- Version: `cartoframes/_version.py`
- Changelog: CHANGELOG.md
- Readme: README.rst

For the QA we recommend running all the guides and examples to check that everything is working OK.

## The developer center "party" (staging)

For every release, the documentation page of the project must be updated: https://carto.com/developers/cartoframes/. It contains:

- Guides: `guides/`
- Reference: `cartoframes/`
- Examples: `examples/`

In the developer center we add the latest micro versions, but all the minors and majors. All the content comes from the [CARTOframes repository](https://github.com/CartoDB/cartoframes), it generates the final docs from markdown files and notebooks based on two configuration documents in the [Developer Center repository](https://github.com/CartoDB/developers):

- Config file: `grunt-tasks/config.js`
- Technologies: `_app/_data/technologies.yml`

The procedure to deploy to staging the documentation of the new release is:

- Create a branch from master
- Update the configuration files:
  - Add new release to `technologies.yml`:
    - A micro release requires updating the micro number from the latest release
    - A minor, or more, release requires to create a new section and update the latest release
  - Point to the release branch in `config.js`, in the `'cartoframes'` section:
    - Comment the tag attribute: `// tag: '...',`
    - Add the release branch: `branch: 'release/M.m.u',`
- Create a pull request pointing to the CARTOframes release branch (this will deploys the Developer Center in a "staging" environment)

After the build is completed, you can check the staging link (it requires VPN access):

`http://{dev-center-branch-name}.developers.website.dev.cartodb.net/developers/cartoframes`

## Publish the release

After testing that everything is OK in the documentation, it's time to create the tag and publish the release:

- Merge the release PR to master
- Create and push a tag `vM.m.u`
- Copy the changelog information in the tag's description
- Publish the package in PyPI
- Merge back the master or the release branch into develop

```
python setup.py sdist bdist_wheel
twine upload dist/*
```

## The docs branch

Then, a docs branch must be created. This is used by the Developer Center, and it allows us to release specific versions of the documentation especially for hotfixes.

```
git checkout -b docs/vM.m.u
git push origin docs/vM.m.u
```

## The developer center "party" (production)

The final step is to deploy the Developer Center to production with the new release of CARTOframes:

- Point to the release branch in `config.js`, in the `'cartoframes'` section:
  - Remove the release branch: `branch: '',`
  - Add the tag attribute: `tag: 'vM.m.u',`
  - Update the releases attribute: `releases: ['vM.m.u', ...`
- Merge the PR to master (this will deploys the Developer Center in a "production" environment)

After the build is completed, you can check the production link (this URL is public):

`https://carto.com/developers/cartoframes/`