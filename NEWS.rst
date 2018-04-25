Changelog
=========

0.6.1
-----

Release 2018-04-18

Updates

- Lowers row limit for lnglat creation to avoid platform limits on SQL API

0.6.0
-----

Release 2018-04-06

Updates

- Fixes a bug where the labels were not always appearing in interactive maps
- Adds the ability to read shared tables (from other users in org accounts) using `CartoContext.read`

0.5.7
-----

Release 2018-03-23

Updates

- Updates MANIFEST.in to properly include asset files for interactive maps in sdist release (#400)

0.5.6
-----

Release 2018-02-26

Updates

- Avoids collision of column names on DO augmentation (#323).

0.5.5
-----

Release 2018-02-13

Updates

- Updates basemap URLs to new CDN

0.5.4
-----

Release 2018-02-06

Updates

- Fixes a bug that prevented creating a table from a Data Observatory augmentation (#375)


0.5.3
-----

Release 2018-01-29

Updates

- Fixes a bug that prevented categorical torque maps to be properly displayed

0.5.2b11
-------

Released 2017-12-20

Updates

- Adds flag to `CartoContext.data_discovery` that excludes non-shoreline-clipped boundary metadata by default

0.5.1b10
-------

Released 2017-12-18

Updates

- Bug fix for overwrite / privacy used in conjunction

0.5.0b9
-------

Released 2017-12-14

Updates

- Adds `CartoContext.data_boundaries`
- `CartoContext.data_discovery` returns non-denominated data
- Expands `CartoContext.data` to do measure lookups based on `geom_refs`
- Expands styling methods to take pre-defined bins
- Adds a compression option for write operations
- Fixes file system path creation to be generic to OS
