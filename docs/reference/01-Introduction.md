##CARTOframes

A Python package for integrating [CARTO](https://carto.com/) maps, analysis, and data services into data science workflows.

Python data analysis workflows often rely on the de facto standards [pandas](http://pandas.pydata.org/) and [Jupyter notebooks](http://jupyter.org/). Integrating CARTO into this workflow saves data scientists time and energy by not having to export datasets as files or retain multiple copies of the data. Instead, CARTOframes give the ability to communicate reproducible analysis while providing the ability to gain from CARTO’s services like hosted, dynamic or static maps and [Data Observatory](https://carto.com/data-observatory/) augmentation.

### Features


*   Write pandas DataFrames to CARTO tables
*   Read CARTO tables and queries into pandas DataFrames
*   Create customizable, interactive CARTO maps in a Jupyter notebook
*   Interact with CARTO’s Data Observatory
*   Use CARTO’s spatially-enabled database for analysis

### Common Uses

*   Visualize spatial data programmatically as matplotlib images or embedded interactive maps
*   Perform cloud-based spatial data processing using CARTO’s analysis tools
*   Extract, transform, and Load (ETL) data using the Python ecosystem for getting data into and out of CARTO
*   Data Services integrations using CARTO’s [Data Observatory](https://carto.com/data-observatory/) and other [Data Services APIs](https://carto.com/location-data-services/)

### More info

*   Complete documentation: [http://cartoframes.readthedocs.io/en/latest/](http://cartoframes.readthedocs.io/en/latest/)
*   Source code: [https://github.com/CartoDB/cartoframes](https://github.com/CartoDB/cartoframes)
*   bug tracker / feature requests: [https://github.com/CartoDB/cartoframes/issues](https://github.com/CartoDB/cartoframes/issues)

Note

cartoframes users must have a CARTO API key for most cartoframes functionality. For example, writing DataFrames to an account, reading from private tables, and visualizing data on maps all require an API key. CARTO provides API keys for education and nonprofit uses, among others. Request access at [support@carto.com](mailto:support%40carto.com). API key access is also given through [GitHub’s Student Developer Pack](https://carto.com/blog/carto-is-part-of-the-github-student-pack).




