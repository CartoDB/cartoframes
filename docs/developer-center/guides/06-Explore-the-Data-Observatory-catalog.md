# Explore the Data Observatory catalog

## Introduction

The Data Observatory is a a spatial data platform that enables Data Scientists to augment their data and broaden their analysis. It offers a wide range of datasets from around the globe in a spatial data repository.

This guide is intended for those who are going to start augmenting their own data using CARTOframes and are willing to explore our public Data Observatory catalog on the seek of the datasets that best fit their use cases and analyses.

**Note: The catalog is public and you don't need a CARTO account to search for available datasets**

## Looking for population data in the US in the catalog

In this guide we are going to filter the Data Observatory catalog looking for population data in the US.

The catalog is comprised of thousands of curated spatial datasets, so when searching for
data the easiest way to find out what you are looking for is make use of a feceted search. A faceted (or hierarchical) search allows you to narrow down search results by applying multiple filters based on faceted classification of the catalog datasets.

Datasets are organized in three main hirearchies:

- Country
- Category
- Geography (or spatial resolution)

For our analysis we are looking for a demographics dataset in the US with a spatial resolution at the level of block groups. 

First we can start for discovering which available geographies (orspatial resolutions) we have for demographics data in the US, by filtering the `catalog` by `country` and `category` and listing the available `geographies`.

Let's start exploring the available categories of data for the US:

```python
from cartoframes.data.observatory import Catalog
Catalog().country('usa').categories
```

Let's filter the geographies by those that contain information at the level of blockgroup. For that purpose we are converting the geographies to a pandas `DataFrame` and search for the string `blockgroup` in the `id` of the geographies:

```python
df = geographies.to_dataframe()
df[df['id'].str.contains('blockgroup', case=False, na=False)]
```

```html
<div class="output_wrapper">
    <div class="output">
        <div class="output_area">
            <div class="prompt output_prompt">Out[1]:</div>
            <div class="output_text output_subarea output_execute_result">
                <pre>[&lt;Category.get('road_traffic')&gt;,
 &lt;Category.get('points_of_interest')&gt;,
 &lt;Category.get('human_mobility')&gt;,
 &lt;Category.get('financial')&gt;,
 &lt;Category.get('environmental')&gt;,
 &lt;Category.get('demographics')&gt;]</pre>
            </div>
        </div>
    </div>
</div>
```

We have three available datasets, from three different providers: Michael Bauer International, Open Data and AGS. For this example, we are going to look for demographic datasets for the AGS blockgroups geography `ags_blockgroup_1c63771c`:

```python
from cartoframes.data.observatory import Catalog
datasets = Catalog().country('usa').category('demographics').geography('ags_blockgroup_1c63771c').datasets
```

**Note that every time you search the catalog you create a new instance of the `Catalog` class**

We have 6 datasets in the US with demographics information at the level of AGS blockgroups:

```python
datasets.to_dataframe()
```

They comprise different information: consumer spending, retail potential, consumer profiles, etc.

At a first sight, it looks the dataset with `data_source_id: sociodemographic` might contain the population information we are looking for. Let's try to understand a little bit better what data this dataset contains by looking at its variables:

```python
from cartoframes.data.observatory import Dataset
Dataset.get('ags_sociodemogr_e92b1637').variables.to_dataframe()
```

