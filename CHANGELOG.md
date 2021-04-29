# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.1] - 2021-04-28

### Changed

- Avoid batch api to carto create table (#1731)

## [1.2.0] - 2021-03-26

### Changed
- Filter only product entities in subscriptions (#1723, #1728)
- Dataset describe not in scientific notation (#1722)
- Review and improve SQLClient utilities (#1725)

### Fixed
- Fix timestamptz read carto (#1720)
- Avoid renaming geometry if geometry name is already GEOM_COLUMN_NAME (#1726)
- Fix user_id in metrics (#1727)

### Removed
- Remove DataObsClient (#1721)

## [1.1.1] - 2021-02-12

### Fixed
- Fix geocoding status columns when using cached parameter (#1717)

## [1.1.0] - 2020-12-04

### Added
- Add new API to delete map publications (#1497)
- Provide Google (Data Observatory) credentials (#1688)

### Changed
- Allow to set a value for null geometries (#1667)
- Add documentation for executing a single test (#1668)
- Add global datasets message in catalog functions (#1670)
- Remove sort by data_range when retrieving isolines (#1673)
- Switch from Travis to Github Actions (#1672)
- Upload table using to_carto in chunks (#1676)
- Check account disk quotas before writing using to_carto (#1674)
- Return GeoDataFrame in the to_dataframe function (#1681)
- Improve metrics for on-prem and staging (#1685)
- Optimize datasets/geographies download (#1693)
- Check geom_coverage and print a message if None (#1695)
- Remove unused BigQueryClient code (#1602)
- Repo clean-up. Refactor docs (#1682)
- Add tests for notebook execution (#1696)
- Mark DataObsClient as deprecated (#1697)
- Review reference (#1699)
- Improve documentation: guides and examples (#1698, #1700, #1704)
- Change iterrows method for index attribute in row data generation (#1706)
- Automatic reprojection in to_carto and Layer (#1708)
- Use regenerate table in replace strategy in to_carto (#1707)

### Fixed
- Remove the batch_size parameter in the call to bulk_geocode (#1666)
- Fix credentials link for set_default_credentials (#1665)
- Fix identifier quoting for columns (#1675, #1678)
- Fix uploading extra the_geom column (#1677)
- Fix wrong username error (#1687)
- Fix empty popups (#1689, #1690)
- Remove None from geometry_types to check validity (#1691)
- Remove nan raw geometries for visualization (#1694)
- Generate carto_geocode_hash with NULL values (#1702)
- Fix formula widget count operation (#1703)

## [1.0.4] - 2020-07-06

### Added
- Add list_tables function (#1649)
- Add catalog public filter to providers, countries and categories (#1658)
- Add set_default_do_credentials function for DO authentication (#1655)

### Changed
- Open publication link in another window (#1647)
- Show a warning when uploading a GeoDataFrame without geometry (#1650)
- Improve GeoDataFrame CRS check, docs and examples (#1656)

### Fixed
- Fix empty geometries issue (#1652)
- Fix Layout publication API key issue (#1654)
- Fix ColumnInfo comparison when replacing a table (#1660)
- Fix formula count (#1662)
- Fix catalog empty output (#1663)

## [1.0.3.1] - 2020-05-19

### Fixed
- Fix read null geoms from carto (#1637)
- Fix show_info in layout maps (#1638)

## [1.0.3] - 2020-05-14

### Added
- Add SQL query param to DO download (#1604, #1618, #1621, #1620)
- Add public filter to catalog (#1623)
- Add providers property to catalog (#1625)
- Add format attribute to map elements (#1626)
- Add download dataset example (#1634)

### Changed
- Require pandas >= 0.25 (#1622)
- Remove enrichment max number of variables restriction from reference (#1624)
- Make Layout interactive by default (#1630)
- UI elements removed in static layout (#1631)
- Improve replace table strategy (#1628, #1633)
- Improve installation guide (#1635)
- Allow multi-selection in category widget

### Fixed
- Scape quotes in SQL function calls (#1619)
- Fix viz palettes (#1627)
- Fix metadata entity request (#1629)

## [1.0.2] - 2020-04-06

### Added
- Add geometry icon to single legends (#1580)
- Publish Layout (#1598)

### Changed
- Use Enrichment API and Metadata API for DO features (#1575, #1594)
- Improve to_csv info message (#1589)
- Use default credentials in metrics (#1603)
- Improve Layout map ordering (#1597)
- Change numeric autoformat (remove scientific notation)
- Return normalized table name in to_carto (#1609)
- Remove empty geometries in Source (#1610)
- Improve docs and examples (#1608, #1611)
- Update catalog info structure (#1612, #1606)

### Fixed
- Allow using columns with symbols in visualization (#1585)
- Fix layer_selector without style helpers (#1580)
- Fix layer_selector in published maps (#1595)
- Fix Google geocoding (#1600)
- Fix legends in Layout (#1597)

## [1.0.1] - 2020-02-28

### Added
- Add encode_data param to Layer (#1536)
- Add WKT case in CSV example (#1545)
- Add Data Management guide (#1547)
- Layer selector in legends (#1551, #1558)
- New 'ascending' parameter to sort numeric legends in ascending or descending order (#1537)

### Changed
- Include user_id in metrics (#1539)
- Disable default param exclusive for isolines (1540)
- Raise an error when trying to visualise a multi-geom GeoDataFrame (#1541)
- Update installation guide structure (#1549)
- Minor examples/guides improvements (#1534, #1552)
- Numeric legends are sorted in descending order by default (#1537)

### Fixed
- Fix legend footer in published maps (#1523)
- Fix default legend for cluster_size_style (#1533)
- Fix DO doc reference generation (#1550)
- Fix get token for Mapbox styles (#1565)

## [1.0.0] - 2020-01-20

[1.0.0 Migration Guide](/docs/developers/migrations/1.0.0.md)

### Added
- Add metrics and utils.setup_metrics function (#1457)
- Add support for Python 3.8 (#1455)
- Add migration guides (#828)

### Changed
- Allow to update a published map (#1451)
- Generate guides from Jupyter Notebooks (#1479)
- Review examples/guides (#1473, #1201, #1500)
- Manage kuviz quota (#1471)
- Explicit map.publish behaviour (#1485)
- Use Airship v2.2 (#1499)

### Fixed
- Replace geometry from geom_col (#1487)
- Fix size_continuous_style/_legend not displaying totals (#1488)

## [1.0rc1] - 2020-01-10

[RC1 Migration Guide](/docs/developers/migrations/rc1.md)

### Added
- Add CLI subscription prompt (#1388)
- Add Data Enrichment e2e tests (#1365)
- Add utils.decode_geometry function (#1418)
- Add legend helpers (#1347, #1442)
- Add style helpers (#1345, #1410)
- Add popup_element helper (#1348)
- Add title and default_* params to Layer class (#1432)
- Add default_legend/widget/popup_element helpers (#1432)

### Changed
- Check quota before using Data Services (#1370)
- Check dependencies on runtime (#1342, #1310)
- Return areas using aggregation None (#1295, #1394)
- Split update_table into rename_table and update_privacy_table (#1380)
- Review subscription messages (#1391, #1407, #1413)
- Remove aggregation in column names, and add variable limit (#1400)
- Update Enrichment filter API (#1374, #1390)
- Rename methods to_csv and to_dataframe (#1396)
- Move widgets helpers to viz (#1349)
- Replace popup param by popup_hover and popup_click in Layer class (#1348, #1432)
- Cartodbfy by default in to_carto (#1416)
- Improve Error messages/docs (#1409)
- Return a GeoDataFrame in every method (#1418)
- Support several agg (#1294)
- Support array in filters (#1406)

### Fixed
- Catch and show Enrichment errors (BQ) (#1364)
- Fix Geography geom_coverage docstring (#1405)
- Fix Geographies not filtered by provider (#1248)
- Fix /support/contribute section in docs (#1427)
- Fix date format when using DataFrames (#1358)
- Fix hover+click behaviour (#1458)
- Fix footer in widgets (#1432)
- Fix dependencies to run in Colab (#1453)

### Removed
- Remove Python 2.7 support (#1324)
- Remove get from CatalogList (#1369)
- Remove CartoDataFrame class (#1418)
- Remove utils.table (#1461)
- Remove default_legend param in Map class (#1399)
- Remove Style, Legend, Widget and Popup classes from viz (#1399)

## [1.0b7] - 2019-12-13
### Added
- Add logger (#1328)
- Add source_col param in Isolines (#1303, #1336)

### Changed
- Improve CartoDataFrame docs (#1307, #1308)
- Do not return cartodb_id in Geocoding/Isolines (#1302)
- Improve installation instruction guide (#1322)
- Publish privacy enhancements (#1286)
- Check if_exists param options (#1325)
- Improve download OpenData (#1309)
- Update DO endpoint (#1311, #1353)
- Improve DO download performance (#1281)
- Update quickstart (#1335, #1351)

### Fixed
- Fix Map default_legend param (#1191)
- Fix column names normalization (#1304)
- Review reference/guides copies (#1299, #1321)
- Display message when Dataset summary is not available (#1208)
- Fix DataObsClient (#1319)
- Fix CartoDataFrame plot (#1339)
- Fix enrichment without subscriptions (#1314)
- Fix encoding detection with all Nones (#1346)

## [1.0b6] - 2019-12-02
### Added
- Add new properties in Catalog Dataset and Geography (#1209)
- Add IO functions and CartoDataFrame class (#1130, #1245)
  - IO functions: read_carto, to_carto, has_table, describe_table,
    update_table, copy_table, create_table_from_query, delete_table.
  - CartoDataFrame class: inherit GeoDataFrame class + from_carto, to_carto, viz.
  - Refactor internals: ContextManager, SourceManager.
- Add index management in upload/download (#1265)
  - read_carto: index_col.
  - to_carto: index, index_label.
  - Improve CDF geometry methods: add set_geometry_from_xy, add geom decoding in
    set_geometry (WKB, EWKB, WKB_HEX, EWKB_HEX, WKB_BHEX, EWKB_BHEX, WKT, EWKT).
- Add geom_col param in upload, enrichment, isolines and visualization (#1270, #1276)
- Add Enrichment/Catalog reference (#1183, #1216)
- Add Discovery Data guide (#996)
- Add Location Data Services guide (#995)
- Add Data Visualization guide (#1251)
- Add Quickstart guide (#966)
- Add Discovery Finantial Data guide (#1263)
- Add Data Enrichment guide (#997)
- Guides review (#1266, #1284)

### Changed
- Optimize local data visualizations size using gzip compression (#1202)
- Optimize enrichment geometry management (#1130)
- Rename CatalogDataset class to Dataset (#1130)
- Validate DO operations (#1228, #1277)
- Validate Dataset/Geometry access (#1256)
- Upload Enrichment data via GCS (#1271)

### Fixed
- Fix Catalog filters (#1229)
- Fix Enrichment columns type issue (#1243, #1268, #1273)

### Removed
- Remove data.Dataset class (#1130)

## [1.0b5] - 2019-11-14
### Added
- Add isolines_layer helper method (#1135, #1159)
- Add range_min/max params to the continuous layer helper methods (#1120)
- Add with_lnglat param to the Isolines service functions (#1134)

### Changed
- Refactor DO Enrichment into classes (#1127, #1137, #1170, #1196)
- Improve Credentials UX (#1028, #776, #1022)
- Optimize local data columns used in the map (#551)

### Fixed
- Fix encoding in data upload (#1133, CartoDB/support#2219)
- Fix dataset.geom_coverage method: (#1153)
- Allow iterables in the breaks param of color_bins_layer (#1146)
- Fix missing link in the documentation (#1150)
- Fix params with value 0 in the helper methods (#971)
- Fix rendering an empty Map (#975)
- Fix viewport in published maps (#1128)
- Restore dataframe after visualization (#1181)
- Fix COPY data types issues (#1190)

## [1.0b4] - 2019-10-25
### Added
- Add support for variable groups in the catalog (#983)
- Add DO token in enrichment (#1020)
- Add Isolines Analysis (#889, #1076, #1070, #1078)
- Add GeoPandas as a dependency (#1047)
- Add subscription for Datasets/Geographies (#1071, #1079)
- Add nested filters for catalog search (#1038, #1069)
- Add list of catalog entities by list of ids or slugs (#1089)
- Download dataset and geographies (#1050)
- Create Maps API key automagically for published maps (#731)
- Add describe methods for CatalogDataset and Variable (#977)
- Add more examples (#1068, #1030, #1115)
- Add cached geocoding (#1066)

### Changed
- Improve reference docs (#841, #1052, #1061, #1024)
- Refactor enrichment functions (#1034, #1043, #1056, #1062, #1085, #1083)
- Use public DO views (#1049)
- Use DataFrame index as cartodb_id (#1072)
- Refactor Catalog using classes (#1044, #1069, #1086, #1093, #1073)
- Rename Geocode class to Geocoding class (#1051)
- Return geocoded dataframes/isolines as geodataframes (#1088, #1092)
- Rename catalog's Dataset to CatalogDataset (#1100)
- Filter datasets by geometry (#1031)
- Improve testing framework (#1060)
- Update data.observatory namespace (#1119)
- Improve guides (#1053)

### Removed
- Remove webcolors dependency (#933)
- Remove carto-python warnings (#1090)
- Remove pandas extension in catalog classes (#1038, #1044)

### Fixed
- Fix popups when using dark basemap (#1099)
- Fix publication using only base_url (#973)

## [1.0b3] - 2019-09-27
### Added
- Add cluster_size_legend helper method (#654)
- Add Layout class to support multiple maps (#892, #953, #919)
- Add dynamic Legend: react to map changes (#935)
- Add LegendList class to allow multiple legends per layer (#925)
- Add more style params to the helper methods (#948)
- Add Discovery API to return DataFrames instances (#960)
- Add Data Discovery properties (#961)
- Add Geocoder Analysis (#888)
- Better integration of the catalog with pandas (#962)
- First stage enrichment polygons (#1016)
- Add DO token (#1019)

### Changed
- Change default_legend behaviour (#775, #774)
- Update namespaces (#911)

### Fixed
- Fix SQLClient & DataObsClient support for set_default_credentials (#876)
- Fix request-URI Too Large for url error (#778)
- Fix sidebar footer overlap (#906)
- Fix histogram widget filter (#929, #940)
- Fix legend title overflow (#928)
- Fix show_info in settings (#918)
- Fix internal state of Dataset (#861)
- Fix retrieving widget type (#954)
- Fix Dataset.upload() with default credentials (#913)
- Fix Dataset.upload() column names using DataFrame (#947, #914, #922)
- Fix min/max Legend values (#939)
- Support uploading DataFrames with non-ascii texts in Python 2 (#1001)

## [1.0b2] - 2019-08-07
### Added
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
- Refactoring Auth API
  - Refactor auth namespace (#789)
  - Deprecate _auth_send (#624)
  - Tables used by a query (#730)
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

### Changed
- Refactor Context API: Credentials (#661)

### Removed
- Clean old API! (#807)

## [1.0b1] - 2019-06-18
### Added
- Sharing visualizations: structure and publication (#745, #740)
- Add namespaces cartoframes.data for Dataset class
- Add support for DataFrames visualization (#735)
- Infer legend prop from the type (#743)
- Use `default_public` as default api key (#744)
- Integrate size legends (#753)
- Add size helpers
  - size_category (#765)
  - size_bins (#652)
  - size_continuous (#653)
- Add multi-layer popups (#793)

### Changed
- Reverse Map layers order (#742)

## [0.10.1] - 2019-06-12
### Fixed
- Fix schema not always properly set in write operations (#734)
- Fix error in Dataset.upload related with array data (#754)
- Fix Dataset.download error when reading boolean column with nulls (#732)

## [0.10.0] - 2019-06-03
### Added
- Add new visualization API (#662)
  - Add Source class (with param detection)
  - Add Dataset methods
    .from_table(...)
    .from_query(...)
    .from_geojson(...)
    .from_dataframe(...)
  - Add set_default_context method
  - Use sources context (credentials, bounds)
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
- Integrate size legends (#721)

### Changed
- Rewrite context.read method using COPY TO (#570)
- Update dependencies (#722)

## [0.9.2] - 2019-03-01
### Changed
- Upgrades CARTO VL version for contrib.vector maps (#546)
- Minor refactors (#545) and doc fixes (#547)

### Fixed
- Fixes a bug where timestamps in LocalLayers raised errors (#550)
- Fixes a bug where multi-layer vector map legends disappeared (#549)

## [0.9.1] - 2019-02-08
### Added
- Adds auto-centering for vector.LocalLayers (#526)

### Changed
- Moves legends to panels instead of sidebars (#531)
- Improves documentation (#522)

## [0.9.0] - 2019-01-09
### Added
- Adds basic legends for CARTO VL maps (#527)
- Adds a line to configure tqdm that prevents dependency issues (#528)

## [0.8.4] - 2018-12-18
### Changed
- Suppresses IFrame warnings temporarily (#524)

### Fixed
- Fixes bug on batch uploads where columns are a subset of util cols (#523)

## [0.8.3] - 2018-12-03
### Fixed
- Adds a module erroneously excluded (#519)

## [0.8.2] - 2018-11-29
### Changed
- Refactors how client id is sent to CARTO Python SDK (#516)

## [0.8.1] - 2018-11-26
### Changed
- Removes unneeded print statement in QueryLayer

## [0.8.0] - 2018-11-15
### Added
- Adds style by line options to Layer and QueryLayer (through cc.map) (#504)
- Adds custom basemap layer to vector maps (#490)

### Changed
- Updates the Mapbox GL and CARTO VL versions for vector maps (#506)
- Multiple documentation updates

### Fixed
- Fixes a problem that prevented vector maps from working with on premises installations (#505)
- Fixes a bug with authorization in on prems (#493)

## [0.7.3] - 2018-10-18
### Changed
- Bump carto-python version that fixes auth api bug

## [0.7.2] - 2018-08-27
### Added
- Adds size option for CARTO VL maps

### Changed
- Bumps Mapbox GL library so vector maps work correctly

## [0.7.1] - 2018-07-16
### Fixed
- Fixes issues where contrib wasn't included in distributions (#469)

## [0.7.0] - 2018-06-22
### Added
- Adds example dataset functionality for example notebook and teaching cartoframes without an account (#382)
- Adds contrib.vector module for bring CARTO VL maps to cartoframes (#446)

### Changed
- Moves BatchJobStatus to its own module (#455)
- Testing updates (#452)

### Removed
- Suppresses warnings emitted from the Carto Python SDK (#456)

### Fixed
- Bug fix for timespans in geometry fetching (#416)
- Base URL validation to avoid issue of POSTs being converted to GETs (#445)

## [0.6.2] - 2018-05-10
### Added
- Adds opacity styling option to Layer and QueryLayer (#440)

## [0.6.1] - 2018-04-18
### Changed
- Lowers row limit for lnglat creation to avoid platform limits on SQL API

## [0.6.0] - 2018-04-06
### Added
- Adds the ability to read shared tables (from other users in org accounts) using `CartoContext.read`

### Fixed
- Fixes a bug where the labels were not always appearing in interactive maps

## [0.5.7] - 2018-03-23
### Changed
- Updates MANIFEST.in to properly include asset files for interactive maps in sdist release (#400)

## [0.5.6] - 2018-02-26
### Fixed
- Avoids collision of column names on DO augmentation (#323).

## [0.5.5] - 2018-02-13
### Changed
- Updates basemap URLs to new CDN

## [0.5.4] - 2018-02-06
### Fixed
- Fixes a bug that prevented creating a table from a Data Observatory augmentation (#375)

## [0.5.3] - 2018-01-29
### Fixed
- Fixes a bug that prevented categorical torque maps to be properly displayed

## [0.5.2b11] - 2017-12-20
### Added
- Adds flag to `CartoContext.data_discovery` that excludes non-shoreline-clipped boundary metadata by default

## [0.5.1b10] - 2017-12-18
### Fixed
- Bug fix for overwrite / privacy used in conjunction

## [0.5.0b9] - 2017-12-14
### Added
- Adds `CartoContext.data_boundaries`
- `CartoContext.data_discovery` returns non-denominated data
- Expands `CartoContext.data` to do measure lookups based on `geom_refs`
- Expands styling methods to take pre-defined bins
- Adds a compression option for write operations

### Fixed
- Fixes file system path creation to be generic to OS
