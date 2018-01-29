Changelog
=========

0.5.3
-----

Release 2017-01-29

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
