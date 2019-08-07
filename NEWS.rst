Changelog
=========

1.0b2
------

Release 2019-xx-xx

Updates

- Dataset improvements
  - Optimize Dataset df/gdf (#704)
  - Decoupling clients from Dataset (#831)
  - Client Architecture (#833)
  - Deprecate cartoframes.analysis.Table in favor of Dataset (#587)
  - Fix retry_times usage in Dataset.download (#783)
  - Strategy pattern, factory pattern and dynamic sources in Dataset (#834)
  - Improve geometry decoding strategy (#798)
  - decode_geometry to support EWKT (#773)
  - Fix RateLimitException in write/upload operations (#804)
- Refactoring AUTH API
  - Refactor auth namespace (#789)
  - deprecate _auth_send (#624)
  - Refactor Context API: Credentials (#661)
  - Clean old API (#807)
  - Tables used by a quer (#730)
- New SQLClient API (#808)
- New Data Observatory API (#806)
- Widgets
  - Define Widget API (#809)
  - Add Histogram Widget (#810)
  - Add Category Widget (#811)
  - Add Animation Control Widget (#812)
  - Add Time Series Widget (#813)
  - Review Widget API (#827)
  - Add Widgets Documentation (#859)
- Helper methods & Map improvements
  - Animation helper method (#657)
  - Implement embed map design (#805)
  - Responsive panel tab shows when there's no legend (#771)
  - Vector legends for small values shouldn't round (#544)
  - Published map not holding viewport settings (#820)
  - geopandas Polygon / MultiPolygon display error
  - Add more params in the existing helpers (#830)
  - Helper methods palette expressions as python lists (#825)
- Documentation and examples (#859, #879, #790, #873)

1.0b1
------

Release 2019-06-18

Updates

- Sharing visualizations: structure and publication (#745, #740)
- Add namespaces cartoframes.data for Dataset class
- Add support for DataFrames visualization (#735)
- Reverse Map layers order (#742)
- Infer legend prop from the type (#743)
- Use `default_public` as default api key (#744)
- Integrate size legends (#753)
- Add size helpers
  - size_category (#765)
  - size_bins (#652)
  - size_continuous (#653)
- Add multi-layer popups (#793)

0.10.1
------

Release 2019-06-12

Updates

- Fix schema not always properly set in write operations (#734)
- Fix error in Dataset.upload related with array data (#754)
- Fix Dataset.download error when reading boolean column with nulls (#732)

0.10.0
------

Release 2019-06-03

Updates

- Rewrite context.read method using COPY TO (#570)
- Add new visualization API (#662)
  - Add Source class (with param detection)
  - Add Dataset methods
    .from_table(...)
    .from_query(...)
    .from_geojson(...)
    .from_dataframe(...)
  - Add set_default_context method
  - Use sources' context (credentials, bounds)
  - Fix Style class API for variables
  - Remove Dataset, SQL, GeoJSON sources
  - Remove sources, contrib namespaces
  - Remove context from Map
  - Update docs in viz classes
  - Add/Update viz tests
  - Pass PEP 8
- Add default style, based on the geom type (#648)
- Add basemap None and color interface (#635)
- Add Popup API (click and hover) (#677)
- Apply default style for not overwritten properties (#684)
- Add namespaces (#683)
  - cartoframes.viz: Map, Layer, Source, Style, Popup, basemaps, helpers
  - cartoframes.auth: Context, set_default_context
- Add color helpers (#692, #651)
  - color_category
  - color_bins
  - color_continuous
- Add center/zoom information (#691)
- Add Legend API (#693)
  - type, prop, title, description, footer
- Update dependencies (#722)
- Integrate size legends (#721)

0.9.2
-----

Release 2019-03-01

Updates

- Upgrades CARTO VL version for contrib.vector maps (#546)
- Fixes a bug where timestamps in LocalLayers raised errors (#550)
- Fixes a bug where multi-layer vector map legends disappeared (#549)
- Minor refactors (#545) and doc fixes (#547)

0.9.1
-----

Release 2019-02-08

Updates

- Moves legends to panels instead of sidebars (#531)
- Adds auto-centering for vector.LocalLayers (#526)
- Improves documentation (#522)

0.9.0
-----

Release 2019-01-09

Updates

- Adds basic legends for CARTO VL maps (#527)
- Adds a line to configure tqdm that prevents dependency issues (#528)

0.8.4
-----

Release 2018-12-18

Updates

- Fixes bug on batch uploads where columns are a subset of util cols (#523)
- Suppresses IFrame warnings temporarily (#524)

0.8.3
-----

Release 2018-12-03

Updates

- Adds a module erroneously excluded (#519)

0.8.2
-----

Release 2018-11-29

Updates

- Refactors how client id is sent to CARTO Python SDK (#516)

0.8.1
-----

Release 2018-11-26

Updates

- Removes unneeded print statement in QueryLayer

0.8.0
-----

Release 2018-11-15

Updates

- Adds style by line options to Layer and QueryLayer (through cc.map) (#504)
- Fixes a problem that prevented vector maps from working with on premises installations (#505)
- Updates the Mapbox GL and CARTO VL versions for vector maps (#506)
- Adds custom basemap layer to vector maps (#490)
- Fixes a bug with authorization in on prems (#493)
- Multiple documentation updates


0.7.3
-----

Release 2018-10-18

Updates

- Bump carto-python version that fixes auth api bug

0.7.2
-----

Release 2018-08-27

Updates

- Adds size option for CARTO VL maps
- Bumps Mapbox GL library so vector maps work correctly

0.7.1
-----

Release 2018-07-16

Updates

- Fixes issues where contrib wasn't included in distributions (#469)

0.7.0
-----

Release 2018-06-22

Updates

- Adds example dataset functionality for example notebook and teaching cartoframes without an account (#382)
- Adds contrib.vector module for bring CARTO VL maps to cartoframes (#446)
- Bug fix for timespans in geometry fetching (#416)
- Suppresses warnings emitted from the Carto Python SDK (#456)
- Moves BatchJobStatus to its own module (#455)
- Testing updates (#452)
- Base URL validation to avoid issue of POSTs being converted to GETs (#445)

0.6.2
-----

Release 2018-05-10

Updates

- Adds opacity styling option to Layer and QueryLayer (#440)

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
