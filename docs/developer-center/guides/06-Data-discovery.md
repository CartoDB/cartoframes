## Data discovery

### Introduction

The Data Observatory is a a spatial data platform that enables Data Scientists to augment their data and broaden their analysis. It offers a wide range of datasets from around the globe in a spatial data repository.

This guide is intended for those who are going to start augmenting their own data using CARTOframes and are willing to explore our public Data Observatory catalog on the seek of the datasets that best fit their use cases and analyses.

**Note: The catalog is public and you don't need a CARTO account to search for available datasets**

### Looking for demographics and financial data in the US in the catalog

In this guide we are going to filter the Data Observatory catalog looking for demographics and financial data in the US.

The catalog is comprised of thousands of curated spatial datasets, so when searching for
data the easiest way to find out what you are looking for is make use of a feceted search. A faceted (or hierarchical) search allows you to narrow down search results by applying multiple filters based on faceted classification of the catalog datasets.

Datasets are organized in three main hirearchies:

- Country
- Category
- Geography (or spatial resolution)

For our analysis we are looking for demographics and financial datasets in the US with a spatial resolution at the level of block groups. 

First we can start for discovering which available geographies (orspatial resolutions) we have for demographics data in the US, by filtering the `catalog` by `country` and `category` and listing the available `geographies`.

Let's start exploring the available categories of data for the US:

```python
from cartoframes.data.observatory import Catalog
Catalog().country('usa').categories
```

<pre class="u-topbottom-Margin"><code>[<Category.get('road_traffic')>,
  <Category.get('points_of_interest')>,
  <Category.get('human_mobility')>,
  <Category.get('financial')>,
  <Category.get('environmental')>,
  <Category.get('demographics')>]
</code></pre>

For the case of the US, the Data Observatory provides six different categories of datasets. Let's discover the available spatial resolutions for the demographics category (which at a first sight will contain the population data we need).

```python
from cartoframes.data.observatory import Catalog
geographies = Catalog().country('usa').category('demographics').geographies
geographies
```

<pre class="u-vertical-scroll u-topbottom-Margin"><code>[<Geography.get('ags_blockgroup_1c63771c')>,
  <Geography.get('ags_q17_4739be4f')>,
  <Geography.get('mbi_blockgroups_1ab060a')>,
  <Geography.get('mbi_counties_141b61cd')>,
  <Geography.get('mbi_county_subd_e8e6ea23')>,
  <Geography.get('mbi_pc_5_digit_4b1682a6')>,
  <Geography.get('od_blockclippe_9c508438')>,
  <Geography.get('od_blockgroupc_3ab29c84')>,
  <Geography.get('od_cbsaclipped_b6a32adc')>,
  <Geography.get('od_censustract_5962fe30')>,
  <Geography.get('od_congression_6774ebb')>,
  <Geography.get('od_countyclipp_caef1ec9')>,
  <Geography.get('od_placeclippe_48a89947')>,
  <Geography.get('od_pumaclipped_b065909')>,
  <Geography.get('od_schooldistr_6d5c417f')>,
  <Geography.get('od_schooldistr_f70c7e28')>,
  <Geography.get('od_schooldistr_75493a16')>,
  <Geography.get('od_stateclippe_8d79f5be')>,
  <Geography.get('od_zcta5clippe_6b6ff33c')>,
  <Geography.get('usct_censustract_784cc2ed')>]
</code></pre>


Let's filter the geographies by those that contain information at the level of blockgroup. For that purpose we are converting the geographies to a pandas `DataFrame` and search for the string `blockgroup` in the `id` of the geographies:


```python
df = geographies.to_dataframe()
df[df['id'].str.contains('blockgroup', case=False, na=False)]
```

<div>
<table border="1" class="dataframe u-vertical-scroll">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>available_in</th>
      <th>country_id</th>
      <th>description</th>
      <th>geom_coverage</th>
      <th>geom_type</th>
      <th>id</th>
      <th>is_public_data</th>
      <th>lang</th>
      <th>name</th>
      <th>provider_id</th>
      <th>provider_name</th>
      <th>slug</th>
      <th>summary_json</th>
      <th>update_frequency</th>
      <th>version</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>[bq]</td>
      <td>usa</td>
      <td>None</td>
      <td>0106000020E61000000800000001030000000100000009...</td>
      <td>MULTIPOLYGON</td>
      <td>carto-do.ags.geography_usa_blockgroup_2015</td>
      <td>False</td>
      <td>eng</td>
      <td>USA Census Block Group</td>
      <td>ags</td>
      <td>Applied Geographic Solutions</td>
      <td>ags_blockgroup_1c63771c</td>
      <td>None</td>
      <td>None</td>
      <td>2015</td>
    </tr>
    <tr>
      <th>2</th>
      <td>None</td>
      <td>usa</td>
      <td>MBI Digital Boundaries for USA at Blockgroups ...</td>
      <td>01060000005A0100000103000000010000002900000013...</td>
      <td>MULTIPOLYGON</td>
      <td>carto-do.mbi.geography_usa_blockgroups_2019</td>
      <td>False</td>
      <td>eng</td>
      <td>USA - Blockgroups</td>
      <td>mbi</td>
      <td>Michael Bauer International</td>
      <td>mbi_blockgroups_1ab060a</td>
      <td>None</td>
      <td>None</td>
      <td>2019</td>
    </tr>
    <tr>
      <th>7</th>
      <td>None</td>
      <td>usa</td>
      <td>None</td>
      <td>0106000020E61000000800000001030000000100000009...</td>
      <td>MULTIPOLYGON</td>
      <td>carto-do-public-data.tiger.geography_usa_block...</td>
      <td>True</td>
      <td>eng</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>open_data</td>
      <td>Open Data</td>
      <td>od_blockgroupc_3ab29c84</td>
      <td>None</td>
      <td>None</td>
      <td>2015</td>
    </tr>
  </tbody>
</table>
</div>

We have three available datasets, from three different providers: Michael Bauer International, Open Data and AGS. For this example, we are going to look for demographic datasets for the AGS blockgroups geography `ags_blockgroup_1c63771c`:

```python
datasets = Catalog().country('usa').category('demographics').geography('ags_blockgroup_1c63771c').datasets
datasets
```

<pre class="u-topbottom-Margin"><code>[<Dataset.get('ags_sociodemogr_e92b1637')>,
    <Dataset.get('ags_consumerspe_fe5d060a')>,
    <Dataset.get('ags_retailpoten_ddf56a1a')>,
    <Dataset.get('ags_consumerpro_e8344e2e')>,
    <Dataset.get('ags_businesscou_a8310a11')>,
    <Dataset.get('ags_crimerisk_9ec89442')>]
</code></pre>

Let's continue with the data discovery. We have 6 datasets in the US with demographics information at the level of AGS blockgroups:

```python
datasets.to_dataframe()
```

<div>
<table border="1" class="dataframe u-vertical-scroll">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>available_in</th>
      <th>category_id</th>
      <th>category_name</th>
      <th>country_id</th>
      <th>data_source_id</th>
      <th>description</th>
      <th>geography_description</th>
      <th>geography_id</th>
      <th>geography_name</th>
      <th>id</th>
      <th>...</th>
      <th>lang</th>
      <th>name</th>
      <th>provider_id</th>
      <th>provider_name</th>
      <th>slug</th>
      <th>summary_json</th>
      <th>temporal_aggregation</th>
      <th>time_coverage</th>
      <th>update_frequency</th>
      <th>version</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>sociodemographic</td>
      <td>Census and ACS sociodemographic data estimated...</td>
      <td>None</td>
      <td>carto-do.ags.geography_usa_blockgroup_2015</td>
      <td>USA Census Block Group</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>...</td>
      <td>eng</td>
      <td>Sociodemographic</td>
      <td>ags</td>
      <td>Applied Geographic Solutions</td>
      <td>ags_sociodemogr_e92b1637</td>
      <td>{'counts': {'rows': 217182, 'cells': 22369746,...</td>
      <td>yearly</td>
      <td>[2019-01-01,2020-01-01)</td>
      <td>None</td>
      <td>2019</td>
    </tr>
    <tr>
      <th>1</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>consumerspending</td>
      <td>The Consumer Expenditure database consists of ...</td>
      <td>None</td>
      <td>carto-do.ags.geography_usa_blockgroup_2015</td>
      <td>USA Census Block Group</td>
      <td>carto-do.ags.demographics_consumerspending_usa...</td>
      <td>...</td>
      <td>eng</td>
      <td>Consumer Spending</td>
      <td>ags</td>
      <td>Applied Geographic Solutions</td>
      <td>ags_consumerspe_fe5d060a</td>
      <td>{'counts': {'rows': 217182, 'cells': 28016478,...</td>
      <td>yearly</td>
      <td>[2018-01-01,2019-01-01)</td>
      <td>None</td>
      <td>2018</td>
    </tr>
    <tr>
      <th>2</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>retailpotential</td>
      <td>The retail potential database consists of aver...</td>
      <td>None</td>
      <td>carto-do.ags.geography_usa_blockgroup_2015</td>
      <td>USA Census Block Group</td>
      <td>carto-do.ags.demographics_retailpotential_usa_...</td>
      <td>...</td>
      <td>eng</td>
      <td>Retail Potential</td>
      <td>ags</td>
      <td>Applied Geographic Solutions</td>
      <td>ags_retailpoten_ddf56a1a</td>
      <td>{'counts': {'rows': 217182, 'cells': 28668024,...</td>
      <td>yearly</td>
      <td>[2018-01-01,2019-01-01)</td>
      <td>None</td>
      <td>2018</td>
    </tr>
    <tr>
      <th>3</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>consumerprofiles</td>
      <td>Segmentation of the population in sixty-eight ...</td>
      <td>None</td>
      <td>carto-do.ags.geography_usa_blockgroup_2015</td>
      <td>USA Census Block Group</td>
      <td>carto-do.ags.demographics_consumerprofiles_usa...</td>
      <td>...</td>
      <td>eng</td>
      <td>Consumer Profiles</td>
      <td>ags</td>
      <td>Applied Geographic Solutions</td>
      <td>ags_consumerpro_e8344e2e</td>
      <td>{'counts': {'rows': 217182, 'cells': 31057026,...</td>
      <td>yearly</td>
      <td>[2018-01-01,2019-01-01)</td>
      <td>None</td>
      <td>2018</td>
    </tr>
    <tr>
      <th>4</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>businesscounts</td>
      <td>Business Counts database is a geographic summa...</td>
      <td>None</td>
      <td>carto-do.ags.geography_usa_blockgroup_2015</td>
      <td>USA Census Block Group</td>
      <td>carto-do.ags.demographics_businesscounts_usa_b...</td>
      <td>...</td>
      <td>eng</td>
      <td>Business Counts</td>
      <td>ags</td>
      <td>Applied Geographic Solutions</td>
      <td>ags_businesscou_a8310a11</td>
      <td>{'counts': {'rows': 217182, 'cells': 25627476,...</td>
      <td>yearly</td>
      <td>[2018-01-01,2019-01-01)</td>
      <td>None</td>
      <td>2018</td>
    </tr>
    <tr>
      <th>5</th>
      <td>[bq]</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>crimerisk</td>
      <td>Using advanced statistical methodologies and a...</td>
      <td>None</td>
      <td>carto-do.ags.geography_usa_blockgroup_2015</td>
      <td>USA Census Block Group</td>
      <td>carto-do.ags.demographics_crimerisk_usa_blockg...</td>
      <td>...</td>
      <td>eng</td>
      <td>Crime Risk</td>
      <td>ags</td>
      <td>Applied Geographic Solutions</td>
      <td>ags_crimerisk_9ec89442</td>
      <td>{'counts': {'rows': 217182, 'cells': 3040548, ...</td>
      <td>yearly</td>
      <td>[2018-01-01,2019-01-01)</td>
      <td>None</td>
      <td>2018</td>
    </tr>
  </tbody>
</table>
<p>6 rows × 21 columns</p>
</div>

They comprise different information: consumer spending, retail potential, consumer profiles, etc.

At a first sight, it looks the dataset with `data_source_id: sociodemographic` might contain the population information we are looking for. Let's try to understand a little bit better what data this dataset contains by looking at its variables:

```python
from cartoframes.data.observatory import Dataset
dataset = Dataset.get('ags_sociodemogr_e92b1637')
variables = dataset.variables
variables
```

<pre class="u-vertical-scroll u-topbottom-Margin"><code>[<Variable.get('HINCYMED65_310bc888')> #'Median Household Income: Age 65-74 (2019A)',
<Variable.get('HINCYMED55_1a269b4b')> #'Median Household Income: Age 55-64 (2019A)',
<Variable.get('HINCYMED45_33daa0a')> #'Median Household Income: Age 45-54 (2019A)',
<Variable.get('HINCYMED35_4c7c3ccd')> #'Median Household Income: Age 35-44 (2019A)',
<Variable.get('HINCYMED25_55670d8c')> #'Median Household Income: Age 25-34 (2019A)',
<Variable.get('HINCYMED24_22603d1a')> #'Median Household Income: Age < 25 (2019A)',
<Variable.get('HINCYGT200_e552a738')> #'Household Income > $200000 (2019A)',
<Variable.get('HINCY6075_1933e114')> #'Household Income $60000-$74999 (2019A)',
<Variable.get('HINCY4550_f7ad7d79')> #'Household Income $45000-$49999 (2019A)',
<Variable.get('HINCY4045_98177a5c')> #'Household Income $40000-$44999 (2019A)',
<Variable.get('HINCY3540_73617481')> #'Household Income $35000-$39999 (2019A)',
<Variable.get('HINCY2530_849c8523')> #'Household Income $25000-$29999 (2019A)',
<Variable.get('HINCY2025_eb268206')> #'Household Income $20000-$24999 (2019A)',
<Variable.get('HINCY1520_8f321b8c')> #'Household Income $15000-$19999 (2019A)',
<Variable.get('HINCY12550_f5b5f848')> #'Household Income $125000-$149999 (2019A)',
<Variable.get('HHSCYMCFCH_9bddf3b1')> #'Families married couple w children (2019A)',
<Variable.get('HHSCYLPMCH_e844cd91')> #'Families male no wife w children (2019A)',
<Variable.get('HHSCYLPFCH_e4112270')> #'Families female no husband children (2019A)',
<Variable.get('HHDCYMEDAG_69c53f22')> #'Median Age of Householder (2019A)',
<Variable.get('HHDCYFAM_85548592')> #'Family Households (2019A)',
<Variable.get('HHDCYAVESZ_f4a95c6f')> #'Average Household Size (2019A)',
<Variable.get('HHDCY_23e8e012')> #'Households (2019A)',
<Variable.get('EDUCYSHSCH_5c444deb')> #'Pop 25+ 9th-12th grade no diploma (2019A)',
<Variable.get('EDUCYLTGR9_cbcfcc89')> #'Pop 25+ less than 9th grade (2019A)',
<Variable.get('EDUCYHSCH_b236c803')> #'Pop 25+ HS graduate (2019A)',
<Variable.get('EDUCYGRAD_d0179ccb')> #'Pop 25+ graduate or prof school degree (2019A)',
<Variable.get('EDUCYBACH_c2295f79')> #'Pop 25+ Bachelors degree (2019A)',
<Variable.get('DWLCYVACNT_4d5e33e9')> #'Housing units vacant (2019A)',
<Variable.get('DWLCYRENT_239f79ae')> #'Occupied units renter (2019A)',
<Variable.get('DWLCYOWNED_a34794a5')> #'Occupied units owner (2019A)',
<Variable.get('AGECYMED_b6eaafb4')> #'Median Age (2019A)',
<Variable.get('AGECYGT85_b9d8a94d')> #'Population age 85+ (2019A)',
<Variable.get('AGECYGT25_433741c7')> #'Population Age 25+ (2019A)',
<Variable.get('AGECYGT15_681a1204')> #'Population Age 15+ (2019A)',
<Variable.get('AGECY8084_b25d4aed')> #'Population age 80-84 (2019A)',
<Variable.get('AGECY7579_15dcf822')> #'Population age 75-79 (2019A)',
<Variable.get('AGECY7074_6da64674')> #'Population age 70-74 (2019A)',
<Variable.get('AGECY6064_cc011050')> #'Population age 60-64 (2019A)',
<Variable.get('AGECY5559_8de3522b')> #'Population age 55-59 (2019A)',
<Variable.get('AGECY5054_f599ec7d')> #'Population age 50-54 (2019A)',
<Variable.get('AGECY4549_2c44040f')> #'Population age 45-49 (2019A)',
<Variable.get('AGECY4044_543eba59')> #'Population age 40-44 (2019A)',
<Variable.get('AGECY3034_86a81427')> #'Population age 30-34 (2019A)',
<Variable.get('AGECY2529_5f75fc55')> #'Population age 25-29 (2019A)',
<Variable.get('AGECY1519_66ed0078')> #'Population age 15-19 (2019A)',
<Variable.get('AGECY0509_c74a565c')> #'Population age 5-9 (2019A)',
<Variable.get('AGECY0004_bf30e80a')> #'Population age 0-4 (2019A)',
<Variable.get('EDUCYSCOLL_1e8c4828')> #'Pop 25+ college no diploma (2019A)',
<Variable.get('MARCYMARR_26e07b7')> #'Now Married (2019A)',
<Variable.get('AGECY2024_270f4203')> #'Population age 20-24 (2019A)',
<Variable.get('AGECY1014_1e97be2e')> #'Population age 10-14 (2019A)',
<Variable.get('AGECY3539_fed2aa71')> #'Population age 35-39 (2019A)',
<Variable.get('EDUCYASSOC_fa1bcf13')> #'Pop 25+ Associate degree (2019A)',
<Variable.get('HINCY1015_d2be7e2b')> #'Household Income $10000-$14999 (2019A)',
<Variable.get('HINCYLT10_745f9119')> #'Household Income < $10000 (2019A)',
<Variable.get('POPPY_946f4ed6')> #'Population (2024A)',
<Variable.get('INCPYMEDHH_e8930404')> #'Median household income (2024A)',
<Variable.get('AGEPYMED_91aa42e6')> #'Median Age (2024A)',
<Variable.get('DWLPY_819e5af0')> #'Housing units (2024A)',
<Variable.get('INCPYAVEHH_6e0d7b43')> #'Average household Income (2024A)',
<Variable.get('INCPYPCAP_ec5fd8ca')> #'Per capita income (2024A)',
<Variable.get('HHDPY_4207a180')> #'Households (2024A)',
<Variable.get('VPHCYNONE_22cb7350')> #'Households: No Vehicle Available (2019A)',
<Variable.get('VPHCYGT1_a052056d')> #'Households: Two or More Vehicles Available (2019A)',
<Variable.get('VPHCY1_53dc760f')> #'Households: One Vehicle Available (2019A)',
<Variable.get('UNECYRATE_b3dc32ba')> #'Unemployment Rate (2019A)',
<Variable.get('SEXCYMAL_ca14d4b8')> #'Population male (2019A)',
<Variable.get('SEXCYFEM_d52acecb')> #'Population female (2019A)',
<Variable.get('RCHCYWHNHS_9206188d')> #'Non Hispanic White (2019A)',
<Variable.get('RCHCYOTNHS_d8592ce9')> #'Non Hispanic Other Race (2019A)',
<Variable.get('RCHCYMUNHS_1a2518ec')> #'Non Hispanic Multiple Race (2019A)',
<Variable.get('RCHCYHANHS_dbe5754')> #'Non Hispanic Hawaiian/Pacific Islander (2019A)',
<Variable.get('RCHCYBLNHS_b5649728')> #'Non Hispanic Black (2019A)',
<Variable.get('RCHCYASNHS_fabeaa31')> #'Non Hispanic Asian (2019A)',
<Variable.get('RCHCYAMNHS_4a788a9d')> #'Non Hispanic American Indian (2019A)',
<Variable.get('POPCYGRPI_147af7a9')> #'Institutional Group Quarters Population (2019A)',
<Variable.get('POPCYGRP_74c19673')> #'Population in Group Quarters (2019A)',
<Variable.get('POPCY_f5800f44')> #'Population (2019A)',
<Variable.get('MARCYWIDOW_7a2977e0')> #'Widowed (2019A)',
<Variable.get('MARCYSEP_9024e7e5')> #'Separated (2019A)',
<Variable.get('MARCYNEVER_c82856b0')> #'Never Married (2019A)',
<Variable.get('MARCYDIVOR_32a11923')> #'Divorced (2019A)',
<Variable.get('LNIEXSPAN_9a19f7f7')> #'SPANISH SPEAKING HOUSEHOLDS',
<Variable.get('LNIEXISOL_d776b2f7')> #'LINGUISTICALLY ISOLATED HOUSEHOLDS (NON-ENGLISH SP...',
<Variable.get('LBFCYUNEM_1e711de4')> #'Pop 16+ civilian unemployed (2019A)',
<Variable.get('LBFCYNLF_c4c98350')> #'Pop 16+ not in labor force (2019A)',
<Variable.get('INCCYMEDHH_bea58257')> #'Median household income (2019A)',
<Variable.get('INCCYMEDFA_59fa177d')> #'Median family income (2019A)',
<Variable.get('INCCYAVEHH_383bfd10')> #'Average household Income (2019A)',
<Variable.get('HUSEXAPT_988f452f')> #'UNITS IN STRUCTURE: 20 OR MORE',
<Variable.get('HUSEX1DET_3684405c')> #'UNITS IN STRUCTURE: 1 DETACHED',
<Variable.get('HOOEXMED_c2d4b5b')> #'Median Value of Owner Occupied Housing Units',
<Variable.get('HISCYHISP_f3b3a31e')> #'Population Hispanic (2019A)',
<Variable.get('HINCYMED75_2810f9c9')> #'Median Household Income: Age 75+ (2019A)',
<Variable.get('HINCY15020_21e894dd')> #'Household Income $150000-$199999 (2019A)',
<Variable.get('BLOCKGROUP_16298bd5')> #'Geographic Identifier',
<Variable.get('LBFCYLBF_59ce7ab0')> #'Population In Labor Force (2019A)',
<Variable.get('LBFCYARM_8c06223a')> #'Pop 16+ in Armed Forces (2019A)',
<Variable.get('DWLCY_e0711b62')> #'Housing units (2019A)',
<Variable.get('LBFCYPOP16_53fa921c')> #'Population Age 16+ (2019A)',
<Variable.get('LBFCYEMPL_c9c22a0')> #'Pop 16+ civilian employed (2019A)',
<Variable.get('INCCYPCAP_691da8ff')> #'Per capita income (2019A)',
<Variable.get('RNTEXMED_2e309f54')> #'Median Cash Rent',
<Variable.get('HINCY3035_4a81d422')> #'Household Income $30000-$34999 (2019A)',
<Variable.get('HINCY5060_62f78b34')> #'Household Income $50000-$59999 (2019A)',
<Variable.get('HINCY10025_665c9060')> #'Household Income $100000-$124999 (2019A)',
<Variable.get('HINCY75100_9d5c69c8')> #'Household Income $75000-$99999 (2019A)',
<Variable.get('AGECY6569_b47bae06')> #'Population age 65-69 (2019A)']
</code></pre>

```python
vdf = variables.to_dataframe()
vdf
```

<div>
<table border="1" class="dataframe u-vertical-scroll">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>agg_method</th>
      <th>column_name</th>
      <th>dataset_id</th>
      <th>db_type</th>
      <th>description</th>
      <th>id</th>
      <th>name</th>
      <th>slug</th>
      <th>starred</th>
      <th>summary_json</th>
      <th>variable_group_id</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>AVG</td>
      <td>HINCYMED65</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Median Household Income: Age 65-74 (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>HINCYMED65</td>
      <td>HINCYMED65_310bc888</td>
      <td>False</td>
      <td>{'head': [67500, 0, 0, 50000, 0, 0, 0, 0, 0, 0...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>1</th>
      <td>AVG</td>
      <td>HINCYMED55</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Median Household Income: Age 55-64 (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>HINCYMED55</td>
      <td>HINCYMED55_1a269b4b</td>
      <td>False</td>
      <td>{'head': [67500, 87500, 0, 30000, 0, 0, 0, 0, ...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>2</th>
      <td>AVG</td>
      <td>HINCYMED45</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Median Household Income: Age 45-54 (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>HINCYMED45</td>
      <td>HINCYMED45_33daa0a</td>
      <td>False</td>
      <td>{'head': [67500, 0, 0, 60000, 0, 0, 0, 0, 0, 0...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>3</th>
      <td>AVG</td>
      <td>HINCYMED35</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Median Household Income: Age 35-44 (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>HINCYMED35</td>
      <td>HINCYMED35_4c7c3ccd</td>
      <td>False</td>
      <td>{'head': [0, 87500, 0, 5000, 0, 0, 0, 0, 0, 0]...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>4</th>
      <td>AVG</td>
      <td>HINCYMED25</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Median Household Income: Age 25-34 (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>HINCYMED25</td>
      <td>HINCYMED25_55670d8c</td>
      <td>False</td>
      <td>{'head': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'tail...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>5</th>
      <td>AVG</td>
      <td>HINCYMED24</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Median Household Income: Age &lt; 25 (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>HINCYMED24</td>
      <td>HINCYMED24_22603d1a</td>
      <td>False</td>
      <td>{'head': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'tail...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>6</th>
      <td>AVG</td>
      <td>HINCYGT200</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Household Income &gt; $200000 (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>HINCYGT200</td>
      <td>HINCYGT200_e552a738</td>
      <td>False</td>
      <td>{'head': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'tail...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>7</th>
      <td>AVG</td>
      <td>HINCY6075</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Household Income $60000-$74999 (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>HINCY6075</td>
      <td>HINCY6075_1933e114</td>
      <td>False</td>
      <td>{'head': [5, 0, 0, 2, 0, 0, 0, 0, 0, 0], 'tail...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>8</th>
      <td>AVG</td>
      <td>HINCY4550</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Household Income $45000-$49999 (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>HINCY4550</td>
      <td>HINCY4550_f7ad7d79</td>
      <td>False</td>
      <td>{'head': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'tail...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>9</th>
      <td>AVG</td>
      <td>HINCY4045</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Household Income $40000-$44999 (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>HINCY4045</td>
      <td>HINCY4045_98177a5c</td>
      <td>False</td>
      <td>{'head': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'tail...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>10</th>
      <td>AVG</td>
      <td>HINCY3540</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Household Income $35000-$39999 (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>HINCY3540</td>
      <td>HINCY3540_73617481</td>
      <td>False</td>
      <td>{'head': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'tail...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>11</th>
      <td>AVG</td>
      <td>HINCY2530</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Household Income $25000-$29999 (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>HINCY2530</td>
      <td>HINCY2530_849c8523</td>
      <td>False</td>
      <td>{'head': [0, 0, 0, 1, 0, 0, 0, 0, 0, 0], 'tail...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>12</th>
      <td>AVG</td>
      <td>HINCY2025</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Household Income $20000-$24999 (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>HINCY2025</td>
      <td>HINCY2025_eb268206</td>
      <td>False</td>
      <td>{'head': [0, 0, 0, 1, 0, 0, 0, 0, 0, 0], 'tail...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>13</th>
      <td>AVG</td>
      <td>HINCY1520</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Household Income $15000-$19999 (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>HINCY1520</td>
      <td>HINCY1520_8f321b8c</td>
      <td>False</td>
      <td>{'head': [0, 0, 0, 1, 0, 0, 0, 0, 0, 0], 'tail...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>14</th>
      <td>AVG</td>
      <td>HINCY12550</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Household Income $125000-$149999 (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>HINCY12550</td>
      <td>HINCY12550_f5b5f848</td>
      <td>False</td>
      <td>{'head': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'tail...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>15</th>
      <td>SUM</td>
      <td>HHSCYMCFCH</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Families married couple w children (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>HHSCYMCFCH</td>
      <td>HHSCYMCFCH_9bddf3b1</td>
      <td>False</td>
      <td>{'head': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'tail...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>16</th>
      <td>SUM</td>
      <td>HHSCYLPMCH</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Families male no wife w children (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>HHSCYLPMCH</td>
      <td>HHSCYLPMCH_e844cd91</td>
      <td>False</td>
      <td>{'head': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'tail...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>17</th>
      <td>SUM</td>
      <td>HHSCYLPFCH</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Families female no husband children (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>HHSCYLPFCH</td>
      <td>HHSCYLPFCH_e4112270</td>
      <td>False</td>
      <td>{'head': [0, 1, 0, 1, 0, 0, 0, 0, 0, 0], 'tail...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>18</th>
      <td>AVG</td>
      <td>HHDCYMEDAG</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>FLOAT</td>
      <td>Median Age of Householder (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>HHDCYMEDAG</td>
      <td>HHDCYMEDAG_69c53f22</td>
      <td>False</td>
      <td>{'head': [61.5, 54, 0, 61.5, 0, 0, 0, 0, 0, 0]...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>19</th>
      <td>SUM</td>
      <td>HHDCYFAM</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Family Households (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>HHDCYFAM</td>
      <td>HHDCYFAM_85548592</td>
      <td>False</td>
      <td>{'head': [1, 2, 0, 6, 0, 0, 0, 0, 0, 0], 'tail...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>20</th>
      <td>AVG</td>
      <td>HHDCYAVESZ</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>FLOAT</td>
      <td>Average Household Size (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>HHDCYAVESZ</td>
      <td>HHDCYAVESZ_f4a95c6f</td>
      <td>False</td>
      <td>{'head': [1.2, 2.5, 0, 2, 0, 0, 0, 0, 0, 0], '...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>21</th>
      <td>SUM</td>
      <td>HHDCY</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Households (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>HHDCY</td>
      <td>HHDCY_23e8e012</td>
      <td>False</td>
      <td>{'head': [5, 2, 0, 11, 0, 0, 0, 0, 0, 0], 'tai...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>22</th>
      <td>SUM</td>
      <td>EDUCYSHSCH</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Pop 25+ 9th-12th grade no diploma (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>EDUCYSHSCH</td>
      <td>EDUCYSHSCH_5c444deb</td>
      <td>False</td>
      <td>{'head': [0, 0, 0, 4, 4, 0, 0, 0, 0, 0], 'tail...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>23</th>
      <td>SUM</td>
      <td>EDUCYLTGR9</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Pop 25+ less than 9th grade (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>EDUCYLTGR9</td>
      <td>EDUCYLTGR9_cbcfcc89</td>
      <td>False</td>
      <td>{'head': [1, 1, 0, 0, 0, 0, 0, 0, 0, 0], 'tail...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>24</th>
      <td>SUM</td>
      <td>EDUCYHSCH</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Pop 25+ HS graduate (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>EDUCYHSCH</td>
      <td>EDUCYHSCH_b236c803</td>
      <td>False</td>
      <td>{'head': [5, 0, 0, 8, 14, 0, 0, 0, 0, 0], 'tai...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>25</th>
      <td>SUM</td>
      <td>EDUCYGRAD</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Pop 25+ graduate or prof school degree (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>EDUCYGRAD</td>
      <td>EDUCYGRAD_d0179ccb</td>
      <td>False</td>
      <td>{'head': [0, 0, 0, 1, 3, 0, 0, 0, 0, 0], 'tail...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>26</th>
      <td>SUM</td>
      <td>EDUCYBACH</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Pop 25+ Bachelors degree (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>EDUCYBACH</td>
      <td>EDUCYBACH_c2295f79</td>
      <td>False</td>
      <td>{'head': [0, 0, 0, 1, 7, 0, 0, 0, 0, 0], 'tail...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>27</th>
      <td>SUM</td>
      <td>DWLCYVACNT</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Housing units vacant (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>DWLCYVACNT</td>
      <td>DWLCYVACNT_4d5e33e9</td>
      <td>False</td>
      <td>{'head': [0, 0, 0, 10, 0, 0, 0, 0, 0, 0], 'tai...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>28</th>
      <td>SUM</td>
      <td>DWLCYRENT</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Occupied units renter (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>DWLCYRENT</td>
      <td>DWLCYRENT_239f79ae</td>
      <td>False</td>
      <td>{'head': [0, 0, 0, 6, 0, 0, 0, 0, 0, 0], 'tail...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>29</th>
      <td>SUM</td>
      <td>DWLCYOWNED</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Occupied units owner (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>DWLCYOWNED</td>
      <td>DWLCYOWNED_a34794a5</td>
      <td>False</td>
      <td>{'head': [5, 2, 0, 5, 0, 0, 0, 0, 0, 0], 'tail...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>78</th>
      <td>SUM</td>
      <td>MARCYWIDOW</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Widowed (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>MARCYWIDOW</td>
      <td>MARCYWIDOW_7a2977e0</td>
      <td>False</td>
      <td>{'head': [0, 0, 0, 2, 0, 0, 0, 0, 0, 0], 'tail...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>79</th>
      <td>SUM</td>
      <td>MARCYSEP</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Separated (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>MARCYSEP</td>
      <td>MARCYSEP_9024e7e5</td>
      <td>False</td>
      <td>{'head': [0, 0, 0, 1, 0, 0, 0, 0, 0, 0], 'tail...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>80</th>
      <td>SUM</td>
      <td>MARCYNEVER</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Never Married (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>MARCYNEVER</td>
      <td>MARCYNEVER_c82856b0</td>
      <td>False</td>
      <td>{'head': [0, 1, 0, 13, 959, 0, 0, 0, 0, 0], 't...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>81</th>
      <td>SUM</td>
      <td>MARCYDIVOR</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Divorced (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>MARCYDIVOR</td>
      <td>MARCYDIVOR_32a11923</td>
      <td>False</td>
      <td>{'head': [0, 0, 0, 4, 0, 0, 0, 0, 0, 0], 'tail...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>82</th>
      <td>SUM</td>
      <td>LNIEXSPAN</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>SPANISH SPEAKING HOUSEHOLDS</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>LNIEXSPAN</td>
      <td>LNIEXSPAN_9a19f7f7</td>
      <td>False</td>
      <td>{'head': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'tail...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>83</th>
      <td>SUM</td>
      <td>LNIEXISOL</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>LINGUISTICALLY ISOLATED HOUSEHOLDS (NON-ENGLIS...</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>LNIEXISOL</td>
      <td>LNIEXISOL_d776b2f7</td>
      <td>False</td>
      <td>{'head': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'tail...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>84</th>
      <td>SUM</td>
      <td>LBFCYUNEM</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Pop 16+ civilian unemployed (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>LBFCYUNEM</td>
      <td>LBFCYUNEM_1e711de4</td>
      <td>False</td>
      <td>{'head': [0, 0, 0, 0, 32, 0, 0, 0, 0, 0], 'tai...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>85</th>
      <td>SUM</td>
      <td>LBFCYNLF</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Pop 16+ not in labor force (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>LBFCYNLF</td>
      <td>LBFCYNLF_c4c98350</td>
      <td>False</td>
      <td>{'head': [6, 1, 0, 10, 581, 0, 0, 0, 0, 0], 't...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>86</th>
      <td>AVG</td>
      <td>INCCYMEDHH</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Median household income (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INCCYMEDHH</td>
      <td>INCCYMEDHH_bea58257</td>
      <td>False</td>
      <td>{'head': [67499, 87499, 0, 27499, 0, 0, 0, 0, ...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>87</th>
      <td>AVG</td>
      <td>INCCYMEDFA</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Median family income (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INCCYMEDFA</td>
      <td>INCCYMEDFA_59fa177d</td>
      <td>False</td>
      <td>{'head': [67499, 87499, 0, 49999, 0, 0, 0, 0, ...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>88</th>
      <td>AVG</td>
      <td>INCCYAVEHH</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Average household Income (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INCCYAVEHH</td>
      <td>INCCYAVEHH_383bfd10</td>
      <td>False</td>
      <td>{'head': [64504, 82566, 0, 33294, 0, 0, 0, 0, ...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>89</th>
      <td>SUM</td>
      <td>HUSEXAPT</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>UNITS IN STRUCTURE: 20 OR MORE</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>HUSEXAPT</td>
      <td>HUSEXAPT_988f452f</td>
      <td>False</td>
      <td>{'head': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'tail...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>90</th>
      <td>SUM</td>
      <td>HUSEX1DET</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>UNITS IN STRUCTURE: 1 DETACHED</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>HUSEX1DET</td>
      <td>HUSEX1DET_3684405c</td>
      <td>False</td>
      <td>{'head': [2, 2, 0, 9, 0, 0, 0, 0, 0, 0], 'tail...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>91</th>
      <td>AVG</td>
      <td>HOOEXMED</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Median Value of Owner Occupied Housing Units</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>HOOEXMED</td>
      <td>HOOEXMED_c2d4b5b</td>
      <td>False</td>
      <td>{'head': [63749, 124999, 0, 74999, 0, 0, 0, 0,...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>92</th>
      <td>SUM</td>
      <td>HISCYHISP</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Population Hispanic (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>HISCYHISP</td>
      <td>HISCYHISP_f3b3a31e</td>
      <td>False</td>
      <td>{'head': [0, 0, 0, 0, 36, 0, 0, 0, 0, 0], 'tai...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>93</th>
      <td>AVG</td>
      <td>HINCYMED75</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Median Household Income: Age 75+ (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>HINCYMED75</td>
      <td>HINCYMED75_2810f9c9</td>
      <td>False</td>
      <td>{'head': [67500, 0, 0, 12500, 0, 0, 0, 0, 0, 0...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>94</th>
      <td>AVG</td>
      <td>HINCY15020</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Household Income $150000-$199999 (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>HINCY15020</td>
      <td>HINCY15020_21e894dd</td>
      <td>False</td>
      <td>{'head': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'tail...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>95</th>
      <td>None</td>
      <td>BLOCKGROUP</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>STRING</td>
      <td>Geographic Identifier</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>BLOCKGROUP</td>
      <td>BLOCKGROUP_16298bd5</td>
      <td>False</td>
      <td>{'head': ['010159819011', '010159819021', '010...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>96</th>
      <td>SUM</td>
      <td>LBFCYLBF</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Population In Labor Force (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>LBFCYLBF</td>
      <td>LBFCYLBF_59ce7ab0</td>
      <td>False</td>
      <td>{'head': [0, 2, 0, 10, 378, 0, 0, 0, 0, 0], 't...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>97</th>
      <td>SUM</td>
      <td>LBFCYARM</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Pop 16+ in Armed Forces (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>LBFCYARM</td>
      <td>LBFCYARM_8c06223a</td>
      <td>False</td>
      <td>{'head': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'tail...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>98</th>
      <td>SUM</td>
      <td>DWLCY</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Housing units (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>DWLCY</td>
      <td>DWLCY_e0711b62</td>
      <td>False</td>
      <td>{'head': [5, 2, 0, 21, 0, 0, 0, 0, 0, 0], 'tai...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>99</th>
      <td>SUM</td>
      <td>LBFCYPOP16</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Population Age 16+ (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>LBFCYPOP16</td>
      <td>LBFCYPOP16_53fa921c</td>
      <td>False</td>
      <td>{'head': [6, 3, 0, 20, 959, 0, 0, 0, 0, 0], 't...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>100</th>
      <td>SUM</td>
      <td>LBFCYEMPL</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Pop 16+ civilian employed (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>LBFCYEMPL</td>
      <td>LBFCYEMPL_c9c22a0</td>
      <td>False</td>
      <td>{'head': [0, 2, 0, 10, 346, 0, 0, 0, 0, 0], 't...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>101</th>
      <td>AVG</td>
      <td>INCCYPCAP</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Per capita income (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INCCYPCAP</td>
      <td>INCCYPCAP_691da8ff</td>
      <td>False</td>
      <td>{'head': [53754, 33026, 0, 16647, 3753, 0, 0, ...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>102</th>
      <td>AVG</td>
      <td>RNTEXMED</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Median Cash Rent</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>RNTEXMED</td>
      <td>RNTEXMED_2e309f54</td>
      <td>False</td>
      <td>{'head': [0, 0, 0, 449, 0, 0, 0, 0, 0, 0], 'ta...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>103</th>
      <td>AVG</td>
      <td>HINCY3035</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Household Income $30000-$34999 (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>HINCY3035</td>
      <td>HINCY3035_4a81d422</td>
      <td>False</td>
      <td>{'head': [0, 0, 0, 1, 0, 0, 0, 0, 0, 0], 'tail...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>104</th>
      <td>AVG</td>
      <td>HINCY5060</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Household Income $50000-$59999 (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>HINCY5060</td>
      <td>HINCY5060_62f78b34</td>
      <td>False</td>
      <td>{'head': [0, 0, 0, 2, 0, 0, 0, 0, 0, 0], 'tail...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>105</th>
      <td>AVG</td>
      <td>HINCY10025</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Household Income $100000-$124999 (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>HINCY10025</td>
      <td>HINCY10025_665c9060</td>
      <td>False</td>
      <td>{'head': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'tail...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>106</th>
      <td>AVG</td>
      <td>HINCY75100</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Household Income $75000-$99999 (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>HINCY75100</td>
      <td>HINCY75100_9d5c69c8</td>
      <td>False</td>
      <td>{'head': [0, 2, 0, 0, 0, 0, 0, 0, 0, 0], 'tail...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>107</th>
      <td>SUM</td>
      <td>AGECY6569</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Population age 65-69 (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>AGECY6569</td>
      <td>AGECY6569_b47bae06</td>
      <td>False</td>
      <td>{'head': [2, 0, 0, 7, 0, 0, 0, 0, 0, 0], 'tail...</td>
      <td>None</td>
    </tr>
  </tbody>
</table>
<p>108 rows × 11 columns</p>
</div>

We can see there are several variables related to population, so this is the `Dataset` we are looking for.

```python
vdf[vdf['description'].str.contains('pop', case=False, na=False)]
```

<div>
<table border="1" class="dataframe u-vertical-scroll">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>agg_method</th>
      <th>column_name</th>
      <th>dataset_id</th>
      <th>db_type</th>
      <th>description</th>
      <th>id</th>
      <th>name</th>
      <th>slug</th>
      <th>starred</th>
      <th>summary_json</th>
      <th>variable_group_id</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>22</th>
      <td>SUM</td>
      <td>EDUCYSHSCH</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Pop 25+ 9th-12th grade no diploma (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>EDUCYSHSCH</td>
      <td>EDUCYSHSCH_5c444deb</td>
      <td>False</td>
      <td>{'head': [0, 0, 0, 4, 4, 0, 0, 0, 0, 0], 'tail...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>23</th>
      <td>SUM</td>
      <td>EDUCYLTGR9</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Pop 25+ less than 9th grade (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>EDUCYLTGR9</td>
      <td>EDUCYLTGR9_cbcfcc89</td>
      <td>False</td>
      <td>{'head': [1, 1, 0, 0, 0, 0, 0, 0, 0, 0], 'tail...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>24</th>
      <td>SUM</td>
      <td>EDUCYHSCH</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Pop 25+ HS graduate (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>EDUCYHSCH</td>
      <td>EDUCYHSCH_b236c803</td>
      <td>False</td>
      <td>{'head': [5, 0, 0, 8, 14, 0, 0, 0, 0, 0], 'tai...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>25</th>
      <td>SUM</td>
      <td>EDUCYGRAD</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Pop 25+ graduate or prof school degree (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>EDUCYGRAD</td>
      <td>EDUCYGRAD_d0179ccb</td>
      <td>False</td>
      <td>{'head': [0, 0, 0, 1, 3, 0, 0, 0, 0, 0], 'tail...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>26</th>
      <td>SUM</td>
      <td>EDUCYBACH</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Pop 25+ Bachelors degree (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>EDUCYBACH</td>
      <td>EDUCYBACH_c2295f79</td>
      <td>False</td>
      <td>{'head': [0, 0, 0, 1, 7, 0, 0, 0, 0, 0], 'tail...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>31</th>
      <td>SUM</td>
      <td>AGECYGT85</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Population age 85+ (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>AGECYGT85</td>
      <td>AGECYGT85_b9d8a94d</td>
      <td>False</td>
      <td>{'head': [1, 0, 0, 2, 2, 0, 0, 0, 0, 0], 'tail...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>32</th>
      <td>SUM</td>
      <td>AGECYGT25</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Population Age 25+ (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>AGECYGT25</td>
      <td>AGECYGT25_433741c7</td>
      <td>False</td>
      <td>{'head': [6, 3, 0, 18, 41, 0, 0, 0, 0, 0], 'ta...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>33</th>
      <td>SUM</td>
      <td>AGECYGT15</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Population Age 15+ (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>AGECYGT15</td>
      <td>AGECYGT15_681a1204</td>
      <td>False</td>
      <td>{'head': [6, 3, 0, 20, 959, 0, 0, 0, 0, 0], 't...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>34</th>
      <td>SUM</td>
      <td>AGECY8084</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Population age 80-84 (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>AGECY8084</td>
      <td>AGECY8084_b25d4aed</td>
      <td>False</td>
      <td>{'head': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'tail...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>35</th>
      <td>SUM</td>
      <td>AGECY7579</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Population age 75-79 (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>AGECY7579</td>
      <td>AGECY7579_15dcf822</td>
      <td>False</td>
      <td>{'head': [0, 0, 0, 1, 0, 0, 0, 0, 0, 0], 'tail...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>36</th>
      <td>SUM</td>
      <td>AGECY7074</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Population age 70-74 (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>AGECY7074</td>
      <td>AGECY7074_6da64674</td>
      <td>False</td>
      <td>{'head': [0, 0, 0, 1, 0, 0, 0, 0, 0, 0], 'tail...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>37</th>
      <td>SUM</td>
      <td>AGECY6064</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Population age 60-64 (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>AGECY6064</td>
      <td>AGECY6064_cc011050</td>
      <td>False</td>
      <td>{'head': [1, 2, 0, 0, 0, 0, 0, 0, 0, 0], 'tail...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>38</th>
      <td>SUM</td>
      <td>AGECY5559</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Population age 55-59 (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>AGECY5559</td>
      <td>AGECY5559_8de3522b</td>
      <td>False</td>
      <td>{'head': [1, 0, 0, 2, 0, 0, 0, 0, 0, 0], 'tail...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>39</th>
      <td>SUM</td>
      <td>AGECY5054</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Population age 50-54 (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>AGECY5054</td>
      <td>AGECY5054_f599ec7d</td>
      <td>False</td>
      <td>{'head': [0, 0, 0, 1, 0, 0, 0, 0, 0, 0], 'tail...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>40</th>
      <td>SUM</td>
      <td>AGECY4549</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Population age 45-49 (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>AGECY4549</td>
      <td>AGECY4549_2c44040f</td>
      <td>False</td>
      <td>{'head': [1, 0, 0, 3, 3, 0, 0, 0, 0, 0], 'tail...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>41</th>
      <td>SUM</td>
      <td>AGECY4044</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Population age 40-44 (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>AGECY4044</td>
      <td>AGECY4044_543eba59</td>
      <td>False</td>
      <td>{'head': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'tail...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>42</th>
      <td>SUM</td>
      <td>AGECY3034</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Population age 30-34 (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>AGECY3034</td>
      <td>AGECY3034_86a81427</td>
      <td>False</td>
      <td>{'head': [0, 0, 0, 0, 5, 0, 0, 0, 0, 0], 'tail...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>43</th>
      <td>SUM</td>
      <td>AGECY2529</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Population age 25-29 (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>AGECY2529</td>
      <td>AGECY2529_5f75fc55</td>
      <td>False</td>
      <td>{'head': [0, 0, 0, 0, 31, 0, 0, 0, 0, 0], 'tai...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>44</th>
      <td>SUM</td>
      <td>AGECY1519</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Population age 15-19 (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>AGECY1519</td>
      <td>AGECY1519_66ed0078</td>
      <td>False</td>
      <td>{'head': [0, 0, 0, 1, 488, 0, 0, 0, 0, 0], 'ta...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>45</th>
      <td>SUM</td>
      <td>AGECY0509</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Population age 5-9 (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>AGECY0509</td>
      <td>AGECY0509_c74a565c</td>
      <td>False</td>
      <td>{'head': [0, 0, 0, 1, 0, 0, 0, 0, 0, 0], 'tail...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>46</th>
      <td>SUM</td>
      <td>AGECY0004</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Population age 0-4 (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>AGECY0004</td>
      <td>AGECY0004_bf30e80a</td>
      <td>False</td>
      <td>{'head': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'tail...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>47</th>
      <td>SUM</td>
      <td>EDUCYSCOLL</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Pop 25+ college no diploma (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>EDUCYSCOLL</td>
      <td>EDUCYSCOLL_1e8c4828</td>
      <td>False</td>
      <td>{'head': [0, 2, 0, 3, 10, 0, 0, 0, 0, 0], 'tai...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>49</th>
      <td>SUM</td>
      <td>AGECY2024</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Population age 20-24 (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>AGECY2024</td>
      <td>AGECY2024_270f4203</td>
      <td>False</td>
      <td>{'head': [0, 0, 0, 1, 430, 0, 0, 0, 0, 0], 'ta...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>50</th>
      <td>SUM</td>
      <td>AGECY1014</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Population age 10-14 (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>AGECY1014</td>
      <td>AGECY1014_1e97be2e</td>
      <td>False</td>
      <td>{'head': [0, 2, 0, 1, 0, 0, 0, 0, 0, 0], 'tail...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>51</th>
      <td>SUM</td>
      <td>AGECY3539</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Population age 35-39 (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>AGECY3539</td>
      <td>AGECY3539_fed2aa71</td>
      <td>False</td>
      <td>{'head': [0, 1, 0, 1, 0, 0, 0, 0, 0, 0], 'tail...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>52</th>
      <td>SUM</td>
      <td>EDUCYASSOC</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Pop 25+ Associate degree (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>EDUCYASSOC</td>
      <td>EDUCYASSOC_fa1bcf13</td>
      <td>False</td>
      <td>{'head': [0, 0, 0, 1, 3, 0, 0, 0, 0, 0], 'tail...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>55</th>
      <td>SUM</td>
      <td>POPPY</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>FLOAT</td>
      <td>Population (2024A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>POPPY</td>
      <td>POPPY_946f4ed6</td>
      <td>False</td>
      <td>{'head': [0, 0, 8, 0, 0, 0, 4, 0, 2, 59], 'tai...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>66</th>
      <td>SUM</td>
      <td>SEXCYMAL</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Population male (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>SEXCYMAL</td>
      <td>SEXCYMAL_ca14d4b8</td>
      <td>False</td>
      <td>{'head': [1, 2, 0, 13, 374, 0, 0, 0, 0, 0], 't...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>67</th>
      <td>SUM</td>
      <td>SEXCYFEM</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Population female (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>SEXCYFEM</td>
      <td>SEXCYFEM_d52acecb</td>
      <td>False</td>
      <td>{'head': [5, 3, 0, 9, 585, 0, 0, 0, 0, 0], 'ta...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>75</th>
      <td>SUM</td>
      <td>POPCYGRPI</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Institutional Group Quarters Population (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>POPCYGRPI</td>
      <td>POPCYGRPI_147af7a9</td>
      <td>False</td>
      <td>{'head': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'tail...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>76</th>
      <td>SUM</td>
      <td>POPCYGRP</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Population in Group Quarters (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>POPCYGRP</td>
      <td>POPCYGRP_74c19673</td>
      <td>False</td>
      <td>{'head': [0, 0, 0, 0, 959, 0, 0, 0, 0, 0], 'ta...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>77</th>
      <td>SUM</td>
      <td>POPCY</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Population (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>POPCY</td>
      <td>POPCY_f5800f44</td>
      <td>False</td>
      <td>{'head': [6, 5, 0, 22, 959, 0, 0, 0, 0, 0], 't...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>84</th>
      <td>SUM</td>
      <td>LBFCYUNEM</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Pop 16+ civilian unemployed (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>LBFCYUNEM</td>
      <td>LBFCYUNEM_1e711de4</td>
      <td>False</td>
      <td>{'head': [0, 0, 0, 0, 32, 0, 0, 0, 0, 0], 'tai...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>85</th>
      <td>SUM</td>
      <td>LBFCYNLF</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Pop 16+ not in labor force (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>LBFCYNLF</td>
      <td>LBFCYNLF_c4c98350</td>
      <td>False</td>
      <td>{'head': [6, 1, 0, 10, 581, 0, 0, 0, 0, 0], 't...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>92</th>
      <td>SUM</td>
      <td>HISCYHISP</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Population Hispanic (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>HISCYHISP</td>
      <td>HISCYHISP_f3b3a31e</td>
      <td>False</td>
      <td>{'head': [0, 0, 0, 0, 36, 0, 0, 0, 0, 0], 'tai...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>96</th>
      <td>SUM</td>
      <td>LBFCYLBF</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Population In Labor Force (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>LBFCYLBF</td>
      <td>LBFCYLBF_59ce7ab0</td>
      <td>False</td>
      <td>{'head': [0, 2, 0, 10, 378, 0, 0, 0, 0, 0], 't...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>97</th>
      <td>SUM</td>
      <td>LBFCYARM</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Pop 16+ in Armed Forces (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>LBFCYARM</td>
      <td>LBFCYARM_8c06223a</td>
      <td>False</td>
      <td>{'head': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'tail...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>99</th>
      <td>SUM</td>
      <td>LBFCYPOP16</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Population Age 16+ (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>LBFCYPOP16</td>
      <td>LBFCYPOP16_53fa921c</td>
      <td>False</td>
      <td>{'head': [6, 3, 0, 20, 959, 0, 0, 0, 0, 0], 't...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>100</th>
      <td>SUM</td>
      <td>LBFCYEMPL</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Pop 16+ civilian employed (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>LBFCYEMPL</td>
      <td>LBFCYEMPL_c9c22a0</td>
      <td>False</td>
      <td>{'head': [0, 2, 0, 10, 346, 0, 0, 0, 0, 0], 't...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>107</th>
      <td>SUM</td>
      <td>AGECY6569</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>INTEGER</td>
      <td>Population age 65-69 (2019A)</td>
      <td>carto-do.ags.demographics_sociodemographic_usa...</td>
      <td>AGECY6569</td>
      <td>AGECY6569_b47bae06</td>
      <td>False</td>
      <td>{'head': [2, 0, 0, 7, 0, 0, 0, 0, 0, 0], 'tail...</td>
      <td>None</td>
    </tr>
  </tbody>
</table>
</div>


We can follow the very same process to discover `financial` datasets, let's see how it works by first listing the geographies available for the category `financial` in the US:


```python
Catalog().country('usa').category('financial').geographies
```




<pre class="u-vertical-scroll u-topbottom-Margin"><code>[<Geography.get('mc_block_9ebc626c')>,
  <Geography.get('mc_blockgroup_c4b8da4c')>,
  <Geography.get('mc_county_31cde2d')>,
  <Geography.get('mc_state_cc31b9d1')>,
  <Geography.get('mc_tract_3704a85c')>,
  <Geography.get('mc_zipcode_263079e3')>]
  </code></pre>



We can clearly identify a geography at the blockgroup resolution, provided by Mastercard:


```python
from cartoframes.data.observatory import Geography
Geography.get('mc_blockgroup_c4b8da4c').to_dict()
```

<pre class="u-vertical-scroll u-topbottom-Margin"><code>{'id': 'carto-do.mastercard.geography_usa_blockgroup_2019',
  'slug': 'mc_blockgroup_c4b8da4c',
  'name': 'USA Census Block Groups',
  'description': None,
  'country_id': 'usa',
  'provider_id': 'mastercard',
  'provider_name': 'Mastercard',
  'lang': 'eng',
  'geom_type': 'MULTIPOLYGON',
  'update_frequency': None,
  'version': '2019',
  'is_public_data': False}
  </code></pre>



Now we can list the available datasets provided by Mastercard for the US Census blockgroups spatial resolution:


```python
Catalog().country('usa').category('financial').geography('mc_blockgroup_c4b8da4c').datasets.to_dataframe()
```

<div>
<table border="1" class="dataframe u-vertical-scroll">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>available_in</th>
      <th>category_id</th>
      <th>category_name</th>
      <th>country_id</th>
      <th>data_source_id</th>
      <th>description</th>
      <th>geography_description</th>
      <th>geography_id</th>
      <th>geography_name</th>
      <th>id</th>
      <th>...</th>
      <th>lang</th>
      <th>name</th>
      <th>provider_id</th>
      <th>provider_name</th>
      <th>slug</th>
      <th>summary_json</th>
      <th>temporal_aggregation</th>
      <th>time_coverage</th>
      <th>update_frequency</th>
      <th>version</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>None</td>
      <td>financial</td>
      <td>Financial</td>
      <td>usa</td>
      <td>mrli</td>
      <td>MRLI scores validate, evaluate and benchmark t...</td>
      <td>None</td>
      <td>carto-do.mastercard.geography_usa_blockgroup_2019</td>
      <td>USA Census Block Groups</td>
      <td>carto-do.mastercard.financial_mrli_usa_blockgr...</td>
      <td>...</td>
      <td>eng</td>
      <td>MRLI Data for Census Block Groups</td>
      <td>mastercard</td>
      <td>Mastercard</td>
      <td>mc_mrli_35402a9d</td>
      <td>{'counts': {'rows': 1072383, 'cells': 22520043...</td>
      <td>monthly</td>
      <td>None</td>
      <td>monthly</td>
      <td>2019</td>
    </tr>
  </tbody>
</table>
<p>1 rows × 21 columns</p>
</div>



Let's finally inspect the variables available in the dataset:


```python
Dataset.get('mc_mrli_35402a9d').variables
```



<pre class="u-vertical-scroll u-topbottom-Margin"><code>[<Variable.get('transactions_st_d22b3489')> #'Same as transactions_score, but only comparing ran...',
  <Variable.get('region_id_3c7d0d92')> #'Region identifier (construction varies depending o...',
  <Variable.get('category_8c84b3a7')> #'Industry/sector categories (Total Retail, Retail e...',
  <Variable.get('month_57cd6f80')> #'Name of the month the data refers to',
  <Variable.get('region_type_d875e9e7')> #'Administrative boundary type (block, block group, ...',
  <Variable.get('stability_state_8af6b92')> #'Same as stability_score, but only comparing rankin...',
  <Variable.get('sales_score_49d02f1e')> #'Rank based on the average monthly sales for the pr...',
  <Variable.get('stability_score_6756cb72')> #'Rank based on the change in merchants between the ...',
  <Variable.get('ticket_size_sta_3bfd5114')> #'Same as ticket_size_score, but only comparing rank...',
  <Variable.get('sales_metro_sco_e088134d')> #'Same as sales_score, but only comparing ranking wi...',
  <Variable.get('transactions_me_628f6065')> #'Same as transactions_score, but only comparing ran...',
  <Variable.get('growth_score_68b3f9ac')> #'Rank based on the percent change in sales between ...',
  <Variable.get('ticket_size_met_8b5905f8')> #'Same as ticket_size_score, but only comparing rank...',
  <Variable.get('ticket_size_sco_21f7820a')> #'Rank based on the average monthly sales for the pr...',
  <Variable.get('growth_state_sc_11870b1c')> #'Same as growth_score, but only comparing ranking w...',
  <Variable.get('stability_metro_b80b3f7e')> #'Same as stability_score, but only comparing rankin...',
  <Variable.get('growth_metro_sc_a1235ff0')> #'Same as growth_score, but only comparing ranking w...',
  <Variable.get('sales_state_sco_502c47a1')> #'Same as sales_score, but only comparing ranking wi...',
  <Variable.get('transactions_sc_ee976f1e')> #'Rank based on the average number of transactions f...']
</code></pre>

### Dataset and variables metadata

The Data Observatory catalog is not only a repository of curated spatial datasets, it also contains valuable information that helps on understanding better the underlying data for every dataset, so you can take an informed decision on what data best fits your problem.

Some of the augmented metadata you can find for each dataset in the catalog is:

- `head` and `tail` methods to get a glimpse of the actual data. This helps you to understand the available columns, data types, etc. To start modelling your problem right away.
- `geom_coverage` to visualize on a map the geographical coverage of the data in the `Dataset`.
- `counts`, `fields_by_type` and a full `describe` method with stats of the actual values in the dataset, such as: average, stdev, quantiles, min, max, median for each of the variables of the dataset.

You don't need a subscription to a dataset to be able to query the augmented metadata, it's just publicly available for anyone exploring the Data Observatory catalog.

Let's overview some of that information, starting by getting a glimpse of the ten first or last rows of the actual data of the dataset:


```python
from cartoframes.data.observatory import Dataset
dataset = Dataset.get('ags_sociodemogr_e92b1637')
```


```python
dataset.head()
```


<div>
<table border="1" class="dataframe u-vertical-scroll">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>DWLCY</th>
      <th>HHDCY</th>
      <th>POPCY</th>
      <th>VPHCY1</th>
      <th>AGECYMED</th>
      <th>HHDCYFAM</th>
      <th>HOOEXMED</th>
      <th>HUSEXAPT</th>
      <th>LBFCYARM</th>
      <th>LBFCYLBF</th>
      <th>...</th>
      <th>MARCYDIVOR</th>
      <th>MARCYNEVER</th>
      <th>MARCYWIDOW</th>
      <th>RCHCYAMNHS</th>
      <th>RCHCYASNHS</th>
      <th>RCHCYBLNHS</th>
      <th>RCHCYHANHS</th>
      <th>RCHCYMUNHS</th>
      <th>RCHCYOTNHS</th>
      <th>RCHCYWHNHS</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>5</td>
      <td>5</td>
      <td>6</td>
      <td>0</td>
      <td>64.00</td>
      <td>1</td>
      <td>63749</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>...</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>6</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>2</td>
      <td>5</td>
      <td>1</td>
      <td>36.50</td>
      <td>2</td>
      <td>124999</td>
      <td>0</td>
      <td>0</td>
      <td>2</td>
      <td>...</td>
      <td>0</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>3</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>2</td>
    </tr>
    <tr>
      <th>2</th>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0.00</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>...</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>21</td>
      <td>11</td>
      <td>22</td>
      <td>4</td>
      <td>64.00</td>
      <td>6</td>
      <td>74999</td>
      <td>0</td>
      <td>0</td>
      <td>10</td>
      <td>...</td>
      <td>4</td>
      <td>13</td>
      <td>2</td>
      <td>0</td>
      <td>0</td>
      <td>22</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>0</td>
      <td>0</td>
      <td>959</td>
      <td>0</td>
      <td>18.91</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>378</td>
      <td>...</td>
      <td>0</td>
      <td>959</td>
      <td>0</td>
      <td>5</td>
      <td>53</td>
      <td>230</td>
      <td>0</td>
      <td>25</td>
      <td>0</td>
      <td>609</td>
    </tr>
    <tr>
      <th>5</th>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0.00</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>...</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
    </tr>
    <tr>
      <th>6</th>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0.00</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>...</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
    </tr>
    <tr>
      <th>7</th>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0.00</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>...</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
    </tr>
    <tr>
      <th>8</th>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0.00</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>...</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
    </tr>
    <tr>
      <th>9</th>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0.00</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>...</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
<p>10 rows × 101 columns</p>
</div>

Alternatively, you can get the last ten ones with `dataset.tail()`

An overview of the coverage of the dataset


```python
dataset.geom_coverage()
```

<iframe
  frameborder="0"
  style="
    border: 1px solid #cfcfcf;
    width: 100%;
    height: 632px;
    "
  srcDoc="
  <!DOCTYPE html>
<html lang=&quot;en&quot;>
<head>
  <title>None</title>
  <meta name=&quot;description&quot; content=&quot;None&quot;>
  <meta name=&quot;viewport&quot; content=&quot;width=device-width, initial-scale=1.0&quot;>
  <meta charset=&quot;UTF-8&quot;>
  <!-- Include CARTO VL JS -->
  <script src=&quot;https://libs.cartocdn.com/carto-vl/v1.4/carto-vl.min.js&quot;></script>
  <!-- Include Mapbox GL JS -->
  <script src=&quot;https://api.tiles.mapbox.com/mapbox-gl-js/v1.0.0/mapbox-gl.js&quot;></script>
  <!-- Include Mapbox GL CSS -->
  <link href=&quot;https://api.tiles.mapbox.com/mapbox-gl-js/v1.0.0/mapbox-gl.css&quot; rel=&quot;stylesheet&quot; />

  <!-- Include Airship -->
  <script nomodule=&quot;&quot; src=&quot;https://libs.cartocdn.com/airship-components/v2.2.0-rc.2.1/airship.js&quot;></script>
  <script type=&quot;module&quot; src=&quot;https://libs.cartocdn.com/airship-components/v2.2.0-rc.2.1/airship/airship.esm.js&quot;></script>
  <script src=&quot;https://libs.cartocdn.com/airship-bridge/v2.2.0-rc.2.1/asbridge.min.js&quot;></script>
  <link href=&quot;https://libs.cartocdn.com/airship-style/v2.2.0-rc.2.1/airship.min.css&quot; rel=&quot;stylesheet&quot;>
  <link href=&quot;https://libs.cartocdn.com/airship-icons/v2.2.0-rc.2.1/icons.css&quot; rel=&quot;stylesheet&quot;>

  <link href=&quot;https://fonts.googleapis.com/css?family=Roboto&quot; rel=&quot;stylesheet&quot; type=&quot;text/css&quot;>

  <!-- External libraries -->

  <!-- pako -->
  <script src=&quot;https://cdnjs.cloudflare.com/ajax/libs/pako/1.0.10/pako_inflate.min.js&quot;></script>

  <!-- html2canvas -->



  <style>
  body {
    margin: 0;
    padding: 0;
  }

  aside.as-sidebar {
    min-width: 300px;
  }

  .map-image {
    display: none;
    max-width: 100%;
    height: auto;
  }
</style>
  <style>
  .map {
    position: absolute;
    height: 100%;
    width: 100%;
  }

  .map-info {
    position: absolute;
    bottom: 0;
    padding: 0 5px;
    background-color: rgba(255, 255, 255, 0.5);
    margin: 0;
    color: rgba(0, 0, 0, 0.75);
    font-size: 12px;
    width: auto;
    height: 18px;
    font-family: 'Open Sans';
  }

  .map-footer {
    background: #F2F6F9;
    font-family: Roboto;
    font-size: 12px;
    line-height: 24px;
    color: #162945;
    text-align: center;
    z-index: 2;
  }

  .map-footer a {
    text-decoration: none;
  }

  .map-footer a:hover {
    text-decoration: underline;
  }
</style>
    <style>
    #error-container {
      position: absolute;
      width: 100%;
      height: 100%;
      background-color: white;
      visibility: hidden;
      padding: 1em;
      font-family: &quot;Courier New&quot;, Courier, monospace;
      margin: 0 auto;
      font-size: 14px;
      overflow: auto;
      z-index: 1000;
      color: black;
    }

    .error-section {
      padding: 1em;
      border-radius: 5px;
      background-color: #fee;
    }

    #error-container #error-highlight {
      font-weight: bold;
      color: inherit;
    }

    #error-container #error-type {
      color: #008000;
    }

    #error-container #error-name {
      color: #ba2121;
    }

    #error-container #error-content {
      margin-top: 0.4em;
    }

    .error-details {
      margin-top: 1em;
    }

    #error-stacktrace {
      list-style: none;
    }
</style>
  <style>
    .popup-content {
      display: flex;
      flex-direction: column;
      padding: 8px;
    }

    .popup-name {
      font-size: 12px;
      font-weight: 400;
      line-height: 20px;
      margin-bottom: 4px;
    }

    .popup-value {
      font-size: 16px;
      font-weight: 600;
      line-height: 20px;
    }

    .popup-value:not(:last-of-type) {
      margin-bottom: 16px;
    }
</style>
  <style>
  as-widget-header .as-widget-header__header {
    margin-bottom: 8px;
    overflow-wrap: break-word;
  }

  as-widget-header .as-widget-header__subheader {
    margin-bottom: 12px;
  }

  as-category-widget {
    max-height: 250px;
  }
</style>
</head>

<body class=&quot;as-app-body as-app&quot;>
  <img id=&quot;map-image&quot; class=&quot;map-image&quot; alt='Static map image' />
  <as-responsive-content id=&quot;main-container&quot;>

    <main class=&quot;as-main&quot;>
      <div class=&quot;as-map-area&quot;>
        <div id=&quot;map&quot; class=&quot;map&quot;></div>


      </div> <!-- as-map-area -->
    </main> <!-- as-main -->
  </as-responsive-content>



  <div id=&quot;error-container&quot; class=&quot;error&quot;>
  <p>There is a <span class=&quot;errors&quot; id=&quot;error-highlight&quot;></span>
  from the <a href=&quot;https://carto.com/developers/carto-vl/&quot; target=&quot;_blank&quot;>CARTO VL</a> library:</p>
  <section class=&quot;error-section&quot;>
    <span class=&quot;errors&quot; id=&quot;error-name&quot;></span>:
    <section id=&quot;error-content&quot;>
      <span class=&quot;errors&quot; id=&quot;error-type&quot;></span>
      <span class=&quot;errors&quot; id=&quot;error-message&quot;></span>
    </section>
  </section>

  <details class=&quot;error-details&quot;>
    <summary>StackTrace</summary>
    <ul id=&quot;error-stacktrace&quot;></ul>
  </details>
</div>
</body>

<script>
  var init = (function () {
  'use strict';

  const BASEMAPS = {
    DarkMatter: carto.basemaps.darkmatter,
    Voyager: carto.basemaps.voyager,
    Positron: carto.basemaps.positron
  };

  const attributionControl = new mapboxgl.AttributionControl({
    compact: false
  });

  const FIT_BOUNDS_SETTINGS = { animate: false, padding: 50, maxZoom: 16 };

  function format(value) {
    if (Array.isArray(value)) {
      const [first, second] = value;
      if (first === -Infinity) {
        return `< ${formatValue(second)}`;
      }
      if (second === Infinity) {
        return `> ${formatValue(first)}`;
      }
      return `${formatValue(first)} - ${formatValue(second)}`;
    }
    return formatValue(value);
  }

  function formatValue(value) {
    if (typeof value === 'number') {
      return formatNumber(value);
    }
    return value;
  }

  function formatNumber(value) {
    const log = Math.log10(Math.abs(value));

    if ((log > 4 || log < -2.00000001) && value) {
      return value.toExponential(2);
    }

    if (!Number.isInteger(value)) {
      return value.toLocaleString(undefined, {
        minimumFractionDigits: 2,
        maximumFractionDigits: 3
      });
    }

    return value.toLocaleString();
  }

  function updateViewport(map) {
    function updateMapInfo() {
      const mapInfo$ = document.getElementById('map-info');
      const center = map.getCenter();
      const lat = center.lat.toFixed(6);
      const lng = center.lng.toFixed(6);
      const zoom = map.getZoom().toFixed(2);

      mapInfo$.innerText = `viewport={'zoom': ${zoom}, 'lat': ${lat}, 'lng': ${lng}}`;
    }

    updateMapInfo();

    map.on('zoom', updateMapInfo);
    map.on('move', updateMapInfo); 
  }

  function getBasecolorSettings(basecolor) {
    return {
      'version': 8,
      'sources': {},
      'layers': [{
          'id': 'background',
          'type': 'background',
          'paint': {
              'background-color': basecolor
          }
      }]
    };
  }

  function getImageElement(mapIndex) {
    const id = mapIndex !== undefined ? `map-image-${mapIndex}` : 'map-image';
    return document.getElementById(id);
  }

  function getContainerElement(mapIndex) {
    const id = mapIndex !== undefined ? `main-container-${mapIndex}` : 'main-container';
    return document.getElementById(id);
  }

  function saveImage(mapIndex) {
    const img = getImageElement(mapIndex);
    const container = getContainerElement(mapIndex);

    html2canvas(container)
      .then((canvas) => setMapImage(canvas, img, container));
  }

  function setMapImage(canvas, img, container) {
    const src = canvas.toDataURL();
    img.setAttribute('src', src);
    img.style.display = 'block';
    container.style.display = 'none';
  }

  function createDefaultLegend(layers) {
    const defaultLegendContainer = document.getElementById('default-legend-container');
    defaultLegendContainer.style.display = 'none';

    AsBridge.VL.Legends.layersLegend(
      '#default-legend',
      layers,
      {
        onLoad: () => defaultLegendContainer.style.display = 'unset'
      }
    );
  }

  function createLegend(layer, legendData, layerIndex, mapIndex=0) {
    const element = document.querySelector(`#layer${layerIndex}_map${mapIndex}_legend`);

    if (legendData.length) {
      legendData.forEach((legend, legendIndex) => _createLegend(layer, legend, layerIndex, legendIndex, mapIndex));
    } else {
      _createLegend(layer, legendData, layerIndex, 0, mapIndex);
    }
  }

  function _createLegend(layer, legend, layerIndex, legendIndex, mapIndex=0) {
    const element = document.querySelector(`#layer${layerIndex}_map${mapIndex}_legend${legendIndex}`);

    if (legend.prop) {
      const othersLabel = 'Others';   // TODO: i18n
      const prop = legend.prop;
      const dynamic = legend.dynamic;
      const variable = legend.variable;
      const config = { othersLabel, variable };
      const options = { format, config, dynamic };

      if (legend.type.startsWith('size-continuous')) {
        config.samples = 4;
      }

      AsBridge.VL.Legends.rampLegend(element, layer, prop, options);
    }
  }

  /** From https://github.com/errwischt/stacktrace-parser/blob/master/src/stack-trace-parser.js */

  /**
   * This parses the different stack traces and puts them into one format
   * This borrows heavily from TraceKit (https://github.com/csnover/TraceKit)
   */

  const UNKNOWN_FUNCTION = '<unknown>';
  const chromeRe = /^\s*at (.*?) ?\(((?:file|https?|blob|chrome-extension|native|eval|webpack|<anonymous>|\/).*?)(?::(\d+))?(?::(\d+))?\)?\s*$/i;
  const chromeEvalRe = /\((\S*)(?::(\d+))(?::(\d+))\)/;
  const winjsRe = /^\s*at (?:((?:\[object object\])?.+) )?\(?((?:file|ms-appx|https?|webpack|blob):.*?):(\d+)(?::(\d+))?\)?\s*$/i;
  const geckoRe = /^\s*(.*?)(?:\((.*?)\))?(?:^|@)((?:file|https?|blob|chrome|webpack|resource|\[native).*?|[^@]*bundle)(?::(\d+))?(?::(\d+))?\s*$/i;
  const geckoEvalRe = /(\S+) line (\d+)(?: > eval line \d+)* > eval/i;

  function parse(stackString) {
    const lines = stackString.split('\n');

    return lines.reduce((stack, line) => {
      const parseResult =
        parseChrome(line) ||
        parseWinjs(line) ||
        parseGecko(line);

      if (parseResult) {
        stack.push(parseResult);
      }

      return stack;
    }, []);
  }

  function parseChrome(line) {
    const parts = chromeRe.exec(line);

    if (!parts) {
      return null;
    }

    const isNative = parts[2] && parts[2].indexOf('native') === 0; // start of line
    const isEval = parts[2] && parts[2].indexOf('eval') === 0; // start of line

    const submatch = chromeEvalRe.exec(parts[2]);
    if (isEval && submatch != null) {
      // throw out eval line/column and use top-most line/column number
      parts[2] = submatch[1]; // url
      parts[3] = submatch[2]; // line
      parts[4] = submatch[3]; // column
    }

    return {
      file: !isNative ? parts[2] : null,
      methodName: parts[1] || UNKNOWN_FUNCTION,
      arguments: isNative ? [parts[2]] : [],
      lineNumber: parts[3] ? +parts[3] : null,
      column: parts[4] ? +parts[4] : null,
    };
  }

  function parseWinjs(line) {
    const parts = winjsRe.exec(line);

    if (!parts) {
      return null;
    }

    return {
      file: parts[2],
      methodName: parts[1] || UNKNOWN_FUNCTION,
      arguments: [],
      lineNumber: +parts[3],
      column: parts[4] ? +parts[4] : null,
    };
  }

  function parseGecko(line) {
    const parts = geckoRe.exec(line);

    if (!parts) {
      return null;
    }

    const isEval = parts[3] && parts[3].indexOf(' > eval') > -1;

    const submatch = geckoEvalRe.exec(parts[3]);
    if (isEval && submatch != null) {
      // throw out eval line/column and use top-most line number
      parts[3] = submatch[1];
      parts[4] = submatch[2];
      parts[5] = null; // no column when eval
    }

    return {
      file: parts[3],
      methodName: parts[1] || UNKNOWN_FUNCTION,
      arguments: parts[2] ? parts[2].split(',') : [],
      lineNumber: parts[4] ? +parts[4] : null,
      column: parts[5] ? +parts[5] : null,
    };
  }

  function displayError(e) {
    const error$ = document.getElementById('error-container');
    const errors$ = error$.getElementsByClassName('errors');
    const stacktrace$ = document.getElementById('error-stacktrace');

    errors$[0].innerHTML = e.name;
    errors$[1].innerHTML = e.name;
    errors$[2].innerHTML = e.type;
    errors$[3].innerHTML = e.message.replace(e.type, '');

    error$.style.visibility = 'visible';

    const stack = parse(e.stack);
    const list = stack.map(item => {
      return `<li>
      at <span class=&quot;stacktrace-method&quot;>${item.methodName}:</span>
      (${item.file}:${item.lineNumber}:${item.column})
    </li>`;
    });

    stacktrace$.innerHTML = list.join('\n');
  }

  function resetPopupClick(interactivity) {
    interactivity.off('featureClick');
  }

  function resetPopupHover(interactivity) {
    interactivity.off('featureHover');
  }

  function setPopupsClick(map, popup, interactivity, attrs) {
    interactivity.on('featureClick', (event) => {
      updatePopup(map, popup, event, attrs);
    });
  }

  function setPopupsHover(map, popup, interactivity, attrs) {
    interactivity.on('featureHover', (event) => {
      updatePopup(map, popup, event, attrs);
    });
  }

  function updatePopup(map, popup, event, attrs) {
    if (event.features.length > 0) {
      let popupHTML = '';
      const layerIDs = [];

      for (const feature of event.features) {
        if (layerIDs.includes(feature.layerId)) {
          continue;
        }
        // Track layers to add only one feature per layer
        layerIDs.push(feature.layerId);

        for (const item of attrs) {
          const variable = feature.variables[item.name];
          if (variable) {
            let value = variable.value;
            value = formatValue(value);

            popupHTML = `
            <span class=&quot;popup-name&quot;>${item.title}</span>
            <span class=&quot;popup-value&quot;>${value}</span>
          ` + popupHTML;
          }
        }
      }

      popup
          .setLngLat([event.coordinates.lng, event.coordinates.lat])
          .setHTML(`<div class=&quot;popup-content&quot;>${popupHTML}</div>`);

      if (!popup.isOpen()) {
        popup.addTo(map);
      }
    } else {
      popup.remove();
    }
  }

  function setInteractivity(map, interactiveLayers, interactiveMapLayers) {
    const interactivity = new carto.Interactivity(interactiveMapLayers);
    const popup = new mapboxgl.Popup({
      closeButton: false,
      closeOnClick: false
    });

    const { clickAttrs, hoverAttrs } = _setInteractivityAttrs(interactiveLayers);

    resetPopupClick(map);
    resetPopupHover(map);

    if (clickAttrs.length > 0) {
      setPopupsClick(map, popup, interactivity, clickAttrs);
    }

    if (hoverAttrs.length > 0) {
      setPopupsHover(map, popup, interactivity, hoverAttrs);
    }
  }

  function _setInteractivityAttrs(interactiveLayers) {
    let clickAttrs = [];
    let hoverAttrs = [];

    interactiveLayers.forEach((interactiveLayer) => {
      interactiveLayer.interactivity.forEach((interactivityDef) => {
        if (interactivityDef.event === 'click') {
          clickAttrs = clickAttrs.concat(interactivityDef.attrs);
        } else if (interactivityDef.event === 'hover') {
          hoverAttrs = hoverAttrs.concat(interactivityDef.attrs);
        }
      });
    });

    return { clickAttrs, hoverAttrs };
  }

  function renderWidget(widget, value) {
    widget.element = widget.element || document.querySelector(`#${widget.id}-value`);

    if (value && widget.element) {
      widget.element.innerText = typeof value === 'number' ? format(value) : value;
    }
  }

  function renderBridge(bridge, widget, mapLayer) {
    widget.element = widget.element || document.querySelector(`#${widget.id}`);

    switch (widget.type) {
      case 'histogram':
        const type = _getWidgetType(mapLayer, widget.value, widget.prop);
        const histogram = type === 'category' ? 'categoricalHistogram' : 'numericalHistogram';
        bridge[histogram](widget.element, widget.value, widget.options);

        break;
      case 'category':
        bridge.category(widget.element, widget.value, widget.options);
        break;
      case 'animation':
        widget.options.propertyName = widget.prop;
        bridge.animationControls(widget.element, widget.value, widget.options);
        break;
      case 'time-series':
        widget.options.propertyName = widget.prop;
        bridge.timeSeries(widget.element, widget.value, widget.options);
        break;
    }
  }

  function bridgeLayerWidgets(map, mapLayer, mapSource, widgets) {
    const bridge = new AsBridge.VL.Bridge({
      carto: carto,
      layer: mapLayer,
      source: mapSource,
      map: map
    });

    widgets
      .filter((widget) => widget.has_bridge)
      .forEach((widget) => renderBridge(bridge, widget, mapLayer));

    bridge.build();
  }

  function _getWidgetType(layer, property, value) {
    return layer.metadata && layer.metadata.properties[value] ?
      layer.metadata.properties[value].type
      : _getWidgetPropertyType(layer, property);
  }

  function _getWidgetPropertyType(layer, property) {
    return layer.metadata && layer.metadata.properties[property] ?
      layer.metadata.properties[property].type
      : null;
  }

  function SourceFactory() {
    const sourceTypes = { GeoJSON, Query, MVT };

    this.createSource = (layer) => {
      return sourceTypes[layer.type](layer);
    };
  }

  function GeoJSON(layer) {
    return new carto.source.GeoJSON(_decodeJSONData(layer.data));
  }

  function Query(layer) {
    const auth = {
      username: layer.credentials.username,
      apiKey: layer.credentials.api_key || 'default_public'
    };

    const config = {
      serverURL: layer.credentials.base_url || `https://${layer.credentials.username}.carto.com/`
    };

    return new carto.source.SQL(layer.data, auth, config);
  }

  function MVT(layer) {
    return new carto.source.MVT(layer.data.file, JSON.parse(layer.data.metadata));
  }

  function _decodeJSONData(b64Data) {
    return JSON.parse(pako.inflate(atob(b64Data), { to: 'string' }));
  }

  const factory = new SourceFactory();

  function initMapLayer(layer, layerIndex, numLayers, hasLegends, map, mapIndex) {
    const mapSource = factory.createSource(layer);
    const mapViz = new carto.Viz(layer.viz);
    const mapLayer = new carto.Layer(`layer${layerIndex}`, mapSource, mapViz);
    const mapLayerIndex = numLayers - layerIndex - 1;

    try {
      mapLayer._updateLayer.catch(displayError);
    } catch (e) {
      throw e;
    }


    mapLayer.addTo(map);

    setLayerLegend(layer, mapLayerIndex, mapLayer, mapIndex, hasLegends);
    setLayerWidgets(map, layer, mapLayer, mapLayerIndex, mapSource);

    return mapLayer;
  }

  function getInteractiveLayers(layers, mapLayers) {
    const interactiveLayers = [];
    const interactiveMapLayers = [];

    layers.forEach((layer, index) => {
      if (layer.interactivity) {
        interactiveLayers.push(layer);
        interactiveMapLayers.push(mapLayers[index]);
      }
    });

    return { interactiveLayers, interactiveMapLayers };
  }

  function setLayerLegend(layer, mapLayerIndex, mapLayer, mapIndex, hasLegends) {
    if (hasLegends && layer.legend) {
      createLegend(mapLayer, layer.legend, mapLayerIndex, mapIndex);
    }
  }

  function setLayerWidgets(map, layer, mapLayer, mapLayerIndex, mapSource) {
    if (layer.widgets.length) {
      initLayerWidgets(layer.widgets, mapLayerIndex);
      updateLayerWidgets(layer.widgets, mapLayer);
      bridgeLayerWidgets(map, mapLayer, mapSource, layer.widgets);
    }
  }

  function initLayerWidgets(widgets, mapLayerIndex) {
    widgets.forEach((widget, widgetIndex) => {
      const id = `layer${mapLayerIndex}_widget${widgetIndex}`;
      widget.id = id;
    });
  }

  function updateLayerWidgets(widgets, mapLayer) {
    mapLayer.on('updated', () => renderLayerWidgets(widgets, mapLayer));
  }

  function renderLayerWidgets(widgets, mapLayer) {
    const variables = mapLayer.viz.variables;

    widgets
      .filter((widget) => !widget.has_bridge)
      .forEach((widget) => {
        const name = widget.variable_name;
        const value = getWidgetValue(name, variables);
        renderWidget(widget, value);
      });
  }

  function getWidgetValue(name, variables) {
    return name && variables[name] ? variables[name].value : null;
  }

  function setReady(settings) {
    try {
      return settings.maps ? initMaps(settings.maps) : initMap(settings);
    } catch (e) {
      displayError(e);
    }
  }

  function initMaps(maps) {
    return maps.map((mapSettings, mapIndex) => {
      return initMap(mapSettings, mapIndex);
    });
  }

  function initMap(settings, mapIndex) {
    const basecolor = getBasecolorSettings(settings.basecolor);
    const basemapStyle =  BASEMAPS[settings.basemap] || settings.basemap || basecolor;
    const container = mapIndex !== undefined ? `map-${mapIndex}` : 'map';
    const map = createMap(container, basemapStyle, settings.bounds, settings.mapboxtoken);

    if (settings.show_info) {
      updateViewport(map);
    }

    if (settings.camera) {
      map.flyTo(settings.camera);
    }

    return initLayers(map, settings, mapIndex);
  }

  function initLayers(map, settings, mapIndex) {
    const numLayers = settings.layers.length;
    const hasLegends = settings.has_legends;
    const isDefaultLegend = settings.default_legend;
    const isStatic = settings.is_static;
    const layers = settings.layers;
    const mapLayers = getMapLayers(
      layers,
      numLayers,
      hasLegends,
      map,
      mapIndex
    );

    createLegend$1(isDefaultLegend, mapLayers);
    setInteractiveLayers(map, layers, mapLayers);

    return waitForMapLayersLoad(isStatic, mapIndex, mapLayers);
  }

  function waitForMapLayersLoad(isStatic, mapIndex, mapLayers) {
    return new Promise((resolve) => {
      carto.on('loaded', mapLayers, onMapLayersLoaded.bind(
        this, isStatic, mapIndex, mapLayers, resolve)
      );
    });
  }

  function onMapLayersLoaded(isStatic, mapIndex, mapLayers, resolve) {
    if (isStatic) {
      saveImage(mapIndex);
    }

    resolve(mapLayers);
  }

  function getMapLayers(layers, numLayers, hasLegends, map, mapIndex) {
    return layers.map((layer, layerIndex) => {
      return initMapLayer(layer, layerIndex, numLayers, hasLegends, map, mapIndex);
    });
  }

  function setInteractiveLayers(map, layers, mapLayers) {
    const { interactiveLayers, interactiveMapLayers } = getInteractiveLayers(layers, mapLayers);

    if (interactiveLayers && interactiveLayers.length > 0) {
      setInteractivity(map, interactiveLayers, interactiveMapLayers);
    }
  }

  function createLegend$1(isDefaultLegend, mapLayers) {
    if (isDefaultLegend) {
      createDefaultLegend(mapLayers);
    }
  }

  function createMap(container, basemapStyle, bounds, accessToken) {
    const map = createMapboxGLMap(container, basemapStyle, accessToken);

    map.addControl(attributionControl);
    map.fitBounds(bounds, FIT_BOUNDS_SETTINGS);

    return map;
  }

  function createMapboxGLMap(container, style, accessToken) {
    if (accessToken) {
      mapboxgl.accessToken = accessToken;
    }

    return new mapboxgl.Map({
      container,
      style,
      zoom: 9,
      dragRotate: false,
      attributionControl: false
    });
  }

  function init(settings) {
    setReady(settings);
  }

  return init;

}());
</script>
<script>
  document
  .querySelector('as-responsive-content')
  .addEventListener('ready', () => {
    const basecolor = '';
    const basemap = 'Positron';
    const bounds = [[-178.438336, -14.601813], [146.154418, 71.440687]];
    const camera = null;
    const default_legend = 'False' === 'true';
    const has_legends = 'False' === 'true';
    const is_static = 'None' === 'true';
    const layers = [{&quot;credentials&quot;: null, &quot;data&quot;: &quot;H4sIAM8z3l0C/21Ty2obQRD8F53Hw/T029dAboHcjQ/GVoxAsYwiH4zRv6dmVhsI0l60qqmtrq7u+dqcPt+3m/vN9+3T6eO4/XbY77fPp93hbVM2vxbsz+b+4WuzewGrAf3/AwDvx8P79njaDeLXuWxet4ff29PxE/9W8o+P/Wn387D/fJ3Cz4fD8WX39nSa2njugmr2pmqlS+U0bvFYHu7Sq3RrWbrWkJbiAyXKqh5MWZgrRWjrE8e3oHvXIq12ydBYcbdgpyJRJVUaT3WtpMwkRbJyCC90C8ASUcQrd6XQiVpFIRGQoZbSF4e3jD/iAD2RgSjNyIvijL0bTTso0Bm2vZhW611taQslYFm6FDAYxvrCV6virlycqkAwFrpQba07cbGs3th4SYEbcORQVGsm6uYKG9rN6cabSl7c3HB56QCGlFuyFfKKvLVNKfOarQ3/gDNTYkXTu/RCCNAzctpEi+RkTANGUyKXNK+U16Iy1NloHFlnsVh1VIhi6HR36XqBmzUzHbBo+rIiEFFi8hgibk3aCl9p/5vWGLuH9oJoqzUKmltC3jB5tox5wEg2ZTmgSl3dDAeYBammrwMm0hSaXyimtJi9XWMxQDKCQmywLBUe1cY3A24aDdMHTCTL7uK3RiaxlD7matjACdtISUZKVlHWZ3g3tde+sSWGy2QjwDAVW3oDrzs2e1w9bFH35So5UuZg0Dve4CYWXDF9wSn4VF1FL1s3ds0kEluBSyuStiRxXXWNAblwdEa/427jRS/94ppo0IDFbG0MMUSSTjZG1Hu/wAlyn7DixrQVvtLGcz4/nv8ChaJ/7AkFAAA=&quot;, &quot;has_legend_list&quot;: false, &quot;interactivity&quot;: [], &quot;legend&quot;: {}, &quot;type&quot;: &quot;GeoJSON&quot;, &quot;viz&quot;: &quot;color: hex(\&quot;#826DBA\&quot;)\nstrokeWidth: ramp(linear(zoom(),2,18),[0.5,1])\nstrokeColor: opacity(#2c2c2c,ramp(linear(zoom(),2,18),[0.2,0.6]))\nopacity: 0.9\n&quot;, &quot;widgets&quot;: []}];
    const mapboxtoken = '';
    const show_info = 'None' === 'true';

    init({
      basecolor,
      basemap,
      bounds,
      camera,
      default_legend,
      has_legends,
      is_static,
      layers,
      mapboxtoken,
      show_info
    });
});
</script>
</html>
">

</iframe>

Some stats about the dataset:

```python
dataset.counts()
```

<pre class="u-topbottom-Margin"><code>rows                    217182
cells                 22369746
null_cells                   0
null_cells_percent           0
dtype: int64
</code></pre>

```python
dataset.fields_by_type()
```

<pre class="u-topbottom-Margin"><code>float       4
string      1
integer    96
dtype: int64
</code></pre>

```python
dataset.describe()
```

<div>
<table border="1" class="dataframe u-vertical-scroll">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>HINCYMED65</th>
      <th>HINCYMED55</th>
      <th>HINCYMED45</th>
      <th>HINCYMED35</th>
      <th>HINCYMED25</th>
      <th>HINCYMED24</th>
      <th>HINCYGT200</th>
      <th>HINCY6075</th>
      <th>HINCY4550</th>
      <th>HINCY4045</th>
      <th>...</th>
      <th>DWLCY</th>
      <th>LBFCYPOP16</th>
      <th>LBFCYEMPL</th>
      <th>INCCYPCAP</th>
      <th>RNTEXMED</th>
      <th>HINCY3035</th>
      <th>HINCY5060</th>
      <th>HINCY10025</th>
      <th>HINCY75100</th>
      <th>AGECY6569</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>avg</th>
      <td>6.195559e+04</td>
      <td>7.513449e+04</td>
      <td>8.297294e+04</td>
      <td>7.907689e+04</td>
      <td>6.610137e+04</td>
      <td>4.765168e+04</td>
      <td>4.236225e+01</td>
      <td>5.938193e+01</td>
      <td>2.406235e+01</td>
      <td>2.483668e+01</td>
      <td>...</td>
      <td>6.420374e+02</td>
      <td>1.218212e+03</td>
      <td>7.402907e+02</td>
      <td>3.451758e+04</td>
      <td>9.315027e+02</td>
      <td>2.416786e+01</td>
      <td>4.542230e+01</td>
      <td>4.876603e+01</td>
      <td>8.272891e+01</td>
      <td>8.051784e+01</td>
    </tr>
    <tr>
      <th>max</th>
      <td>3.500000e+05</td>
      <td>3.500000e+05</td>
      <td>3.500000e+05</td>
      <td>3.500000e+05</td>
      <td>3.500000e+05</td>
      <td>3.500000e+05</td>
      <td>4.812000e+03</td>
      <td>3.081000e+03</td>
      <td>9.530000e+02</td>
      <td>1.293000e+03</td>
      <td>...</td>
      <td>2.800700e+04</td>
      <td>4.707100e+04</td>
      <td>3.202300e+04</td>
      <td>2.898428e+06</td>
      <td>3.999000e+03</td>
      <td>7.290000e+02</td>
      <td>1.981000e+03</td>
      <td>3.231000e+03</td>
      <td>4.432000e+03</td>
      <td>7.777000e+03</td>
    </tr>
    <tr>
      <th>min</th>
      <td>0.000000e+00</td>
      <td>0.000000e+00</td>
      <td>0.000000e+00</td>
      <td>0.000000e+00</td>
      <td>0.000000e+00</td>
      <td>0.000000e+00</td>
      <td>0.000000e+00</td>
      <td>0.000000e+00</td>
      <td>0.000000e+00</td>
      <td>0.000000e+00</td>
      <td>...</td>
      <td>0.000000e+00</td>
      <td>0.000000e+00</td>
      <td>0.000000e+00</td>
      <td>0.000000e+00</td>
      <td>0.000000e+00</td>
      <td>0.000000e+00</td>
      <td>0.000000e+00</td>
      <td>0.000000e+00</td>
      <td>0.000000e+00</td>
      <td>0.000000e+00</td>
    </tr>
    <tr>
      <th>sum</th>
      <td>1.345564e+10</td>
      <td>1.631786e+10</td>
      <td>1.802023e+10</td>
      <td>1.717408e+10</td>
      <td>1.435603e+10</td>
      <td>1.034909e+10</td>
      <td>9.200319e+06</td>
      <td>1.289669e+07</td>
      <td>5.225909e+06</td>
      <td>5.394080e+06</td>
      <td>...</td>
      <td>1.394390e+08</td>
      <td>2.645738e+08</td>
      <td>1.607778e+08</td>
      <td>7.496597e+09</td>
      <td>2.023056e+08</td>
      <td>5.248825e+06</td>
      <td>9.864907e+06</td>
      <td>1.059110e+07</td>
      <td>1.796723e+07</td>
      <td>1.748702e+07</td>
    </tr>
    <tr>
      <th>range</th>
      <td>3.500000e+05</td>
      <td>3.500000e+05</td>
      <td>3.500000e+05</td>
      <td>3.500000e+05</td>
      <td>3.500000e+05</td>
      <td>3.500000e+05</td>
      <td>4.812000e+03</td>
      <td>3.081000e+03</td>
      <td>9.530000e+02</td>
      <td>1.293000e+03</td>
      <td>...</td>
      <td>2.800700e+04</td>
      <td>4.707100e+04</td>
      <td>3.202300e+04</td>
      <td>2.898428e+06</td>
      <td>3.999000e+03</td>
      <td>7.290000e+02</td>
      <td>1.981000e+03</td>
      <td>3.231000e+03</td>
      <td>4.432000e+03</td>
      <td>7.777000e+03</td>
    </tr>
    <tr>
      <th>stdev</th>
      <td>3.377453e+04</td>
      <td>4.102797e+04</td>
      <td>4.392996e+04</td>
      <td>3.932575e+04</td>
      <td>2.741347e+04</td>
      <td>2.948443e+04</td>
      <td>7.601699e+01</td>
      <td>4.940854e+01</td>
      <td>2.227745e+01</td>
      <td>2.245616e+01</td>
      <td>...</td>
      <td>4.051570e+02</td>
      <td>8.107703e+02</td>
      <td>5.421818e+02</td>
      <td>2.302276e+04</td>
      <td>4.772473e+02</td>
      <td>2.167522e+01</td>
      <td>3.882000e+01</td>
      <td>4.946218e+01</td>
      <td>7.159705e+01</td>
      <td>5.888055e+01</td>
    </tr>
    <tr>
      <th>q1</th>
      <td>3.625000e+04</td>
      <td>4.285700e+04</td>
      <td>4.785700e+04</td>
      <td>4.833300e+04</td>
      <td>4.454500e+04</td>
      <td>2.625000e+04</td>
      <td>0.000000e+00</td>
      <td>2.400000e+01</td>
      <td>8.000000e+00</td>
      <td>8.000000e+00</td>
      <td>...</td>
      <td>3.740000e+02</td>
      <td>6.930000e+02</td>
      <td>3.920000e+02</td>
      <td>1.910900e+04</td>
      <td>5.520000e+02</td>
      <td>7.000000e+00</td>
      <td>1.700000e+01</td>
      <td>1.500000e+01</td>
      <td>3.400000e+01</td>
      <td>4.300000e+01</td>
    </tr>
    <tr>
      <th>q3</th>
      <td>6.228300e+04</td>
      <td>7.596200e+04</td>
      <td>8.415200e+04</td>
      <td>8.030300e+04</td>
      <td>6.890600e+04</td>
      <td>4.916700e+04</td>
      <td>2.600000e+01</td>
      <td>5.900000e+01</td>
      <td>2.400000e+01</td>
      <td>2.500000e+01</td>
      <td>...</td>
      <td>6.230000e+02</td>
      <td>1.172000e+03</td>
      <td>7.150000e+02</td>
      <td>3.351600e+04</td>
      <td>9.250000e+02</td>
      <td>2.400000e+01</td>
      <td>4.500000e+01</td>
      <td>4.600000e+01</td>
      <td>8.000000e+01</td>
      <td>7.800000e+01</td>
    </tr>
    <tr>
      <th>median</th>
      <td>4.937500e+04</td>
      <td>5.916700e+04</td>
      <td>6.571400e+04</td>
      <td>6.375000e+04</td>
      <td>5.700000e+04</td>
      <td>3.750000e+04</td>
      <td>8.000000e+00</td>
      <td>4.000000e+01</td>
      <td>1.500000e+01</td>
      <td>1.600000e+01</td>
      <td>...</td>
      <td>4.860000e+02</td>
      <td>9.090000e+02</td>
      <td>5.350000e+02</td>
      <td>2.615000e+04</td>
      <td>7.190000e+02</td>
      <td>1.500000e+01</td>
      <td>3.000000e+01</td>
      <td>3.000000e+01</td>
      <td>5.600000e+01</td>
      <td>5.900000e+01</td>
    </tr>
    <tr>
      <th>interquartile_range</th>
      <td>2.603300e+04</td>
      <td>3.310500e+04</td>
      <td>3.629500e+04</td>
      <td>3.197000e+04</td>
      <td>2.436100e+04</td>
      <td>2.291700e+04</td>
      <td>2.600000e+01</td>
      <td>3.500000e+01</td>
      <td>1.600000e+01</td>
      <td>1.700000e+01</td>
      <td>...</td>
      <td>2.490000e+02</td>
      <td>4.790000e+02</td>
      <td>3.230000e+02</td>
      <td>1.440700e+04</td>
      <td>3.730000e+02</td>
      <td>1.700000e+01</td>
      <td>2.800000e+01</td>
      <td>3.100000e+01</td>
      <td>4.600000e+01</td>
      <td>3.500000e+01</td>
    </tr>
  </tbody>
</table>
<p>10 rows × 107 columns</p>
</div>



Every `Dataset` instance in the catalog contains other useful metadata:

- slug: A short ID
- name and description: Free text attributes
- country
- geography: Every dataset is related to a Geography instance
- category
- provider
- data source
- lang
- temporal aggregation
- time coverage
- update frequency
- version
- is_public_data: whether you need a license to use the dataset for enrichment purposes or not


```python
dataset.to_dict()
```

<pre class="u-vertical-scroll u-topbottom-Margin"><code>{
  'id': 'carto-do.ags.demographics_sociodemographic_usa_blockgroup_2015_yearly_2019',
  'slug': 'ags_sociodemogr_e92b1637',
  'name': 'Sociodemographic',
  'description': 'Census and ACS sociodemographic data estimated for the current year and data projected to five years. Projected fields are general aggregates (total population, total households, median age, avg income etc.)',
  'country_id': 'usa',
  'geography_id': 'carto-do.ags.geography_usa_blockgroup_2015',
  'geography_name': 'USA Census Block Group',
  'geography_description': None,
  'category_id': 'demographics',
  'category_name': 'Demographics',
  'provider_id': 'ags',
  'provider_name': 'Applied Geographic Solutions',
  'data_source_id': 'sociodemographic',
  'lang': 'eng',
  'temporal_aggregation': 'yearly',
  'time_coverage': '[2019-01-01,2020-01-01)',
  'update_frequency': None,
  'version': '2019',
  'is_public_data': False
}
</code></pre>

There's also some intersting metadata, for each variable in the dataset:

- id
- slug: A short ID
- name and description
- column_name: Actual column name in the table that contains the data
- db_type: SQL type in the database
- dataset_id
- agg_method: Aggregation method used
- temporal aggregation and time coverage

Variables are the most important asset in the catalog and when exploring datasets in the Data Observatory catalog it's very important that you understand clearly what variables are available to enrich your own data.

For each `Variable` in each dataset, the Data Observatory provides (as it does with datasets) a set of methods and attributes to understand their underlaying data.

Some of them are:

- `head` and `tail` methods to get a glimpse of the actual data and start modelling your problem right away.
- `counts`, `quantiles` and a full `describe` method with stats of the actual values in the dataset, such as: average, stdev, quantiles, min, max, median for each of the variables of the dataset.
- an `histogram` plot with the distribution of the values on each variable.

Let's overview some of that augmented metadata for the variables in the AGS population dataset.

```python
from cartoframes.data.observatory import Variable
variable = Variable.get('POPPY_946f4ed6')
variable
```

<pre class="u-topbottom-Margin"><code>
  <Variable.get('POPPY_946f4ed6')> #'Population (2024A)'
</code></pre>

```python
variable.to_dict()
```

<pre class="u-topbottom-Margin"><code>{'id': 'carto-do.ags.demographics_sociodemographic_usa_blockgroup_2015_yearly_2019.POPPY',
    'slug': 'POPPY_946f4ed6',
    'name': 'POPPY',
    'description': 'Population (2024A)',
    'column_name': 'POPPY',
    'db_type': 'FLOAT',
    'dataset_id': 'carto-do.ags.demographics_sociodemographic_usa_blockgroup_2015_yearly_2019',
    'agg_method': 'SUM',
    'variable_group_id': None,
    'starred': False}
</code></pre>

There's also some utility methods ot understand the underlying data for each variable:

```python
variable.head()
```

<pre class="u-topbottom-Margin"><code>0     0
1     0
2     8
3     0
4     0
5     0
6     4
7     0
8     2
9    59
dtype: int64
</code></pre>

```python
variable.counts()
```

<pre class="u-topbottom-Margin"><code>all                 217182.000000
null                     0.000000
zero                   303.000000
extreme               9380.000000
distinct              6947.000000
outliers             27571.000000
null_percent             0.000000
zero_percent             0.139514
extreme_percent          0.043190
distinct_percent         3.198700
outliers_percent         0.126949
dtype: float64
</code></pre>

```python
variable.quantiles()
```

<pre class="u-topbottom-Margin"><code>
q1                      867
q3                     1490
median                 1149
interquartile_range     623
dtype: int64
</code></pre>

```python
variable.histogram()
```

![png](../../img/guides/explore_data_observatory_catalog_files/explore_data_observatory_catalog_37_0.png)

```python
variable.describe()
```

<pre class="u-topbottom-Margin"><code>avg                    1.564793e+03
    max                    7.127400e+04
    min                    0.000000e+00
    sum                    3.398448e+08
    range                  7.127400e+04
    stdev                  1.098193e+03
    q1                     8.670000e+02
    q3                     1.490000e+03
    median                 1.149000e+03
    interquartile_range    6.230000e+02
    dtype: float64
</code></pre>

### Subscribe to a Dataset in the catalog

Once you have explored the catalog and have detected a dataset with the variables you need for your analysis and the right spatial resolution, you have to look at the `is_public_data` to know if you can just use it from CARTOframes or you first need to subscribe for a license.

Subscriptions to datasets allow you to use them from CARTOframes to enrich your own data or to download them. See the enrichment guides for more information about this.

Let's see the dataset and geography in our previous example:

```python
dataset = Dataset.get('ags_sociodemogr_e92b1637')
```

```python
dataset.is_public_data
```

<pre class="u-topbottom-Margin"><code>False
</code></pre>

```python
from cartoframes.data.observatory import Geography
geography = Geography.get(dataset.geography)
```

```python
geography.is_public_data
```

<pre class="u-topbottom-Margin"><code>False
</code></pre>

Both `dataset` and `geography` are not public data, that means you need a subscription to be able to use them to enrich your own data.

**To subscribe to data in the Data Observatory catalog you need a CARTO account with access to Data Observatory. See the [credentials](/developers/cartoframes/guides/Authentication/#the-config-file) guide for more info on this topic.**


```python
from cartoframes.auth import set_default_credentials
set_default_credentials('creds.json')
dataset.subscribe()
```

![png](../../img/guides/explore_data_observatory_catalog_files/sub_dat.png)


```python
geography.subscribe()
```

![png](../../img/guides/explore_data_observatory_catalog_files/sub_geo.png)


**Licenses to data in the Data Observatory grant you the right to use the data subscribed for the period of one year. Every dataset or geography you want to use to enrich your own data, as lons as they are not public data, require a valid license.**

You can check the actual status of your subscriptions directly from the catalog.

```python
Catalog().subscriptions()
```

<pre class="u-topbottom-Margin"><code>Datasets: None
Geographies: None
</code></pre>


### About nested filters in the Catalog instance

**Note that every time you search the catalog you create a new instance of the `Catalog` class. Alternatively, when applying `country`, `category` and `geography` filters a catalog instance, you can reuse the same instance of the `catalog` by using the `catalog.clean_filters()` method.**

So for example, if you've filtered the catalog this way:


```python
catalog = Catalog()
catalog.country('usa').category('demographics').datasets
```

<pre class="u-vertical-scroll u-topbottom-Margin"><code>[<Dataset.get('od_acs_181619a3')>,
  <Dataset.get('od_acs_38016c42')>,
  <Dataset.get('od_acs_1f614ee8')>,
  <Dataset.get('od_acs_c6bf32c9')>,
  <Dataset.get('od_acs_91ff81e3')>,
  <Dataset.get('od_acs_13345497')>,
  <Dataset.get('od_acs_87fa66db')>,
  <Dataset.get('od_acs_b98db80e')>,
  <Dataset.get('od_acs_9f4d1f13')>,
  <Dataset.get('od_acs_5b67fbbf')>,
  <Dataset.get('od_acs_29664073')>,
  <Dataset.get('od_acs_4bb9b377')>,
  <Dataset.get('od_acs_9df157a1')>,
  <Dataset.get('od_acs_550657ce')>,
  <Dataset.get('od_tiger_19a6dc83')>,
  <Dataset.get('od_acs_6e4b69f6')>,
  <Dataset.get('od_acs_1a22afad')>,
  <Dataset.get('od_acs_9510981d')>,
  <Dataset.get('od_acs_6d43ed82')>,
  <Dataset.get('od_acs_dc3cfd0f')>,
  <Dataset.get('od_acs_194c5960')>,
  <Dataset.get('od_acs_9a9c93b8')>,
  <Dataset.get('od_acs_7b2649a9')>,
  <Dataset.get('od_acs_478c37b8')>,
  <Dataset.get('od_acs_f98ddfce')>,
  <Dataset.get('od_acs_8b00f653')>,
  <Dataset.get('od_acs_d52a0635')>,
  <Dataset.get('od_acs_1deaa51')>,
  <Dataset.get('od_acs_e0f5ff55')>,
  <Dataset.get('od_acs_52710085')>,
  <Dataset.get('od_acs_b3eac6e8')>,
  <Dataset.get('od_acs_e9e3046f')>,
  <Dataset.get('od_acs_506e3e6a')>,
  <Dataset.get('od_acs_b4cbd26')>,
  <Dataset.get('od_acs_fc07c6c5')>,
  <Dataset.get('od_acs_a1083df8')>,
  <Dataset.get('od_tiger_3336cbf')>,
  <Dataset.get('od_acs_1a09274c')>,
  <Dataset.get('od_tiger_66b9092c')>,
  <Dataset.get('od_acs_db9898c5')>,
  <Dataset.get('od_acs_670c8beb')>,
  <Dataset.get('od_acs_6926adef')>,
  <Dataset.get('mbi_population_678f3375')>,
  <Dataset.get('mbi_retail_spen_e2c1988e')>,
  <Dataset.get('mbi_retail_spen_14142fb4')>,
  <Dataset.get('ags_sociodemogr_e92b1637')>,
  <Dataset.get('ags_consumerspe_fe5d060a')>,
  <Dataset.get('od_acs_e8a7d88d')>,
  <Dataset.get('od_acs_60614ff2')>,
  <Dataset.get('od_acs_f09b24f4')>,
  <Dataset.get('od_acs_1cfa643a')>,
  <Dataset.get('od_acs_c4a00c26')>,
  <Dataset.get('od_acs_c1c86582')>,
  <Dataset.get('od_acs_5b8fdefd')>,
  <Dataset.get('mbi_population_341ee33b')>,
  <Dataset.get('od_spielmansin_5d03106a')>,
  <Dataset.get('mbi_households__109a963')>,
  <Dataset.get('od_acs_c2868f47')>,
  <Dataset.get('od_acs_b581bfd1')>,
  <Dataset.get('od_acs_2d438a42')>,
  <Dataset.get('od_acs_aa92e673')>,
  <Dataset.get('od_acs_1db77442')>,
  <Dataset.get('od_acs_f3eaa128')>,
  <Dataset.get('od_tiger_e5e51d96')>,
  <Dataset.get('od_tiger_41814018')>,
  <Dataset.get('od_tiger_b0608dc7')>,
  <Dataset.get('ags_retailpoten_ddf56a1a')>,
  <Dataset.get('ags_consumerpro_e8344e2e')>,
  <Dataset.get('ags_businesscou_a8310a11')>,
  <Dataset.get('od_acs_5c10acf4')>,
  <Dataset.get('mbi_households__45067b14')>,
  <Dataset.get('od_acs_d28e63ff')>,
  <Dataset.get('ags_sociodemogr_e128078d')>,
  <Dataset.get('ags_crimerisk_9ec89442')>,
  <Dataset.get('od_acs_a9825694')>,
  <Dataset.get('od_tiger_5e55275d')>,
  <Dataset.get('od_acs_a665f9e1')>,
  <Dataset.get('od_acs_5ec6965e')>,
  <Dataset.get('od_acs_f2f40516')>,
  <Dataset.get('od_acs_1209a7e9')>,
  <Dataset.get('od_acs_6c9090b5')>,
  <Dataset.get('od_acs_f9681e48')>,
  <Dataset.get('od_acs_8c8516b')>,
  <Dataset.get('od_acs_59534db1')>,
  <Dataset.get('od_acs_57d06d64')>,
  <Dataset.get('od_acs_6bfd54ac')>,
  <Dataset.get('od_tiger_f9247903')>,
  <Dataset.get('od_acs_abd63a91')>,
  <Dataset.get('mbi_households__981be2e8')>,
  <Dataset.get('od_acs_e1b123b7')>,
  <Dataset.get('od_acs_c31e5f28')>,
  <Dataset.get('od_tiger_476ce2e9')>,
  <Dataset.get('od_tiger_fac69779')>,
  <Dataset.get('od_tiger_384d0b09')>,
  <Dataset.get('od_acs_7c4b8db0')>,
  <Dataset.get('od_acs_eaf66737')>,
  <Dataset.get('od_lodes_b4b9dfac')>,
  <Dataset.get('od_acs_17667f64')>,
  <Dataset.get('od_acs_8c6d324a')>,
  <Dataset.get('od_acs_d60f0d6e')>,
  <Dataset.get('od_tiger_e10059f')>,
  <Dataset.get('od_acs_4f56aa89')>,
  <Dataset.get('od_acs_d9e8a21b')>,
  <Dataset.get('od_acs_c5eb4b5e')>,
  <Dataset.get('od_acs_de856602')>,
  <Dataset.get('od_acs_5978c550')>,
  <Dataset.get('mbi_purchasing__53ab279d')>,
  <Dataset.get('mbi_purchasing__d7fd187')>,
  <Dataset.get('mbi_consumer_sp_54c4abc3')>,
  <Dataset.get('mbi_sociodemogr_b5516832')>,
  <Dataset.get('mbi_households__c943a740')>,
  <Dataset.get('mbi_households__d75b838')>,
  <Dataset.get('mbi_population_d3c82409')>,
  <Dataset.get('mbi_education_53d49ab0')>,
  <Dataset.get('mbi_education_5139bb8a')>,
  <Dataset.get('mbi_education_ecd69207')>,
  <Dataset.get('mbi_consumer_sp_b6a3b235')>,
  <Dataset.get('mbi_consumer_sp_9f31484d')>,
  <Dataset.get('mbi_households__1de12da2')>,
  <Dataset.get('mbi_households__b277b08f')>,
  <Dataset.get('mbi_consumer_pr_8e977645')>,
  <Dataset.get('mbi_retail_spen_ab162703')>,
  <Dataset.get('mbi_retail_spen_c31f0ba0')>,
  <Dataset.get('mbi_retail_cent_eab3bd00')>,
  <Dataset.get('mbi_retail_turn_705247a')>,
  <Dataset.get('mbi_purchasing__31cd621')>,
  <Dataset.get('mbi_purchasing__b27dd930')>,
  <Dataset.get('mbi_consumer_pr_31957ef2')>,
  <Dataset.get('mbi_consumer_pr_55b2234f')>,
  <Dataset.get('mbi_consumer_pr_68d1265a')>,
  <Dataset.get('mbi_population_d88d3bc2')>,
  <Dataset.get('mbi_education_20063878')>,
  <Dataset.get('mbi_retail_cent_55b1b5b7')>,
  <Dataset.get('mbi_sociodemogr_285eaf93')>,
  <Dataset.get('mbi_sociodemogr_bd619b07')>,
  <Dataset.get('mbi_retail_turn_b8072ccd')>,
  <Dataset.get('mbi_sociodemogr_975ca724')>,
  <Dataset.get('mbi_consumer_sp_9a1ba82')>,
  <Dataset.get('mbi_households__be0ba1d4')>
]
</code></pre>

And now you want to take the `financial` datasets for the use, you should:

1. Create a new instance of the catalog: `catalog = Catalog()`
2. Call to `catalog.clean_filters()` over the existing instance.

Another point to remark is that, altough a recommended way to discover data is nesting filters over a `Catalog` instance, you don't need to follow the complete hierarchy (`country`, `category`, `geography`) to list the available datasets.

Alternatively, you can just list all the datasets in the `US` or list all the datasets for the `demographics` category, and continue exploring the catalog locally with pandas.

Let's see an example of that, in which we filter public data for the `demographics` category world wide:

```python
df = Catalog().category('demographics').datasets.to_dataframe()
df[df['is_public_data'] == True]
```

<div>
<table border="1" class="dataframe u-vertical-scroll">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>available_in</th>
      <th>category_id</th>
      <th>category_name</th>
      <th>country_id</th>
      <th>data_source_id</th>
      <th>description</th>
      <th>geography_description</th>
      <th>geography_id</th>
      <th>geography_name</th>
      <th>id</th>
      <th>...</th>
      <th>lang</th>
      <th>name</th>
      <th>provider_id</th>
      <th>provider_name</th>
      <th>slug</th>
      <th>summary_json</th>
      <th>temporal_aggregation</th>
      <th>time_coverage</th>
      <th>update_frequency</th>
      <th>version</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>8</th>
      <td>None</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>acs</td>
      <td>None</td>
      <td>None</td>
      <td>carto-do-public-data.tiger.geography_usa_pumac...</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>carto-do-public-data.acs.demographics_acs_usa_...</td>
      <td>...</td>
      <td>eng</td>
      <td>American Community Survey (ACS) data at pumacl...</td>
      <td>open_data</td>
      <td>Open Data</td>
      <td>od_acs_181619a3</td>
      <td>None</td>
      <td>5yrs</td>
      <td>[2010-01-01,2014-01-01)</td>
      <td>None</td>
      <td>20102014</td>
    </tr>
    <tr>
      <th>9</th>
      <td>None</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>acs</td>
      <td>None</td>
      <td>None</td>
      <td>carto-do-public-data.tiger.geography_usa_place...</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>carto-do-public-data.acs.demographics_acs_usa_...</td>
      <td>...</td>
      <td>eng</td>
      <td>American Community Survey (ACS) data at placec...</td>
      <td>open_data</td>
      <td>Open Data</td>
      <td>od_acs_38016c42</td>
      <td>None</td>
      <td>yearly</td>
      <td>[2017-01-01,2018-01-01)</td>
      <td>None</td>
      <td>2017</td>
    </tr>
    <tr>
      <th>10</th>
      <td>None</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>acs</td>
      <td>None</td>
      <td>None</td>
      <td>carto-do-public-data.tiger.geography_usa_count...</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>carto-do-public-data.acs.demographics_acs_usa_...</td>
      <td>...</td>
      <td>eng</td>
      <td>American Community Survey (ACS) data at county...</td>
      <td>open_data</td>
      <td>Open Data</td>
      <td>od_acs_1f614ee8</td>
      <td>None</td>
      <td>5yrs</td>
      <td>[2010-01-01,2014-01-01)</td>
      <td>None</td>
      <td>20102014</td>
    </tr>
    <tr>
      <th>13</th>
      <td>None</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>acs</td>
      <td>None</td>
      <td>None</td>
      <td>carto-do-public-data.tiger.geography_usa_pumac...</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>carto-do-public-data.acs.demographics_acs_usa_...</td>
      <td>...</td>
      <td>eng</td>
      <td>American Community Survey (ACS) data at pumacl...</td>
      <td>open_data</td>
      <td>Open Data</td>
      <td>od_acs_c6bf32c9</td>
      <td>None</td>
      <td>5yrs</td>
      <td>[2013-01-01,2018-01-01)</td>
      <td>None</td>
      <td>20132017</td>
    </tr>
    <tr>
      <th>14</th>
      <td>None</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>acs</td>
      <td>None</td>
      <td>None</td>
      <td>carto-do-public-data.tiger.geography_usa_block...</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>carto-do-public-data.acs.demographics_acs_usa_...</td>
      <td>...</td>
      <td>eng</td>
      <td>American Community Survey (ACS) data at blockg...</td>
      <td>open_data</td>
      <td>Open Data</td>
      <td>od_acs_91ff81e3</td>
      <td>None</td>
      <td>5yrs</td>
      <td>[2010-01-01,2014-01-01)</td>
      <td>None</td>
      <td>20102014</td>
    </tr>
    <tr>
      <th>16</th>
      <td>None</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>acs</td>
      <td>None</td>
      <td>None</td>
      <td>carto-do-public-data.tiger.geography_usa_place...</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>carto-do-public-data.acs.demographics_acs_usa_...</td>
      <td>...</td>
      <td>eng</td>
      <td>American Community Survey (ACS) data at placec...</td>
      <td>open_data</td>
      <td>Open Data</td>
      <td>od_acs_13345497</td>
      <td>None</td>
      <td>5yrs</td>
      <td>[2011-01-01,2015-01-01)</td>
      <td>None</td>
      <td>20112015</td>
    </tr>
    <tr>
      <th>17</th>
      <td>None</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>acs</td>
      <td>None</td>
      <td>None</td>
      <td>carto-do-public-data.tiger.geography_usa_place...</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>carto-do-public-data.acs.demographics_acs_usa_...</td>
      <td>...</td>
      <td>eng</td>
      <td>American Community Survey (ACS) data at placec...</td>
      <td>open_data</td>
      <td>Open Data</td>
      <td>od_acs_87fa66db</td>
      <td>None</td>
      <td>5yrs</td>
      <td>[2013-01-01,2018-01-01)</td>
      <td>None</td>
      <td>20132017</td>
    </tr>
    <tr>
      <th>20</th>
      <td>None</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>acs</td>
      <td>None</td>
      <td>None</td>
      <td>carto-do-public-data.tiger.geography_usa_zcta5...</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>carto-do-public-data.acs.demographics_acs_usa_...</td>
      <td>...</td>
      <td>eng</td>
      <td>American Community Survey (ACS) data at zcta5c...</td>
      <td>open_data</td>
      <td>Open Data</td>
      <td>od_acs_b98db80e</td>
      <td>None</td>
      <td>5yrs</td>
      <td>[2011-01-01,2015-01-01)</td>
      <td>None</td>
      <td>20112015</td>
    </tr>
    <tr>
      <th>21</th>
      <td>None</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>acs</td>
      <td>None</td>
      <td>None</td>
      <td>carto-do-public-data.tiger.geography_usa_schoo...</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>carto-do-public-data.acs.demographics_acs_usa_...</td>
      <td>...</td>
      <td>eng</td>
      <td>American Community Survey (ACS) data at school...</td>
      <td>open_data</td>
      <td>Open Data</td>
      <td>od_acs_9f4d1f13</td>
      <td>None</td>
      <td>5yrs</td>
      <td>[2010-01-01,2014-01-01)</td>
      <td>None</td>
      <td>20102014</td>
    </tr>
    <tr>
      <th>22</th>
      <td>None</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>acs</td>
      <td>None</td>
      <td>None</td>
      <td>carto-do-public-data.tiger.geography_usa_pumac...</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>carto-do-public-data.acs.demographics_acs_usa_...</td>
      <td>...</td>
      <td>eng</td>
      <td>American Community Survey (ACS) data at pumacl...</td>
      <td>open_data</td>
      <td>Open Data</td>
      <td>od_acs_5b67fbbf</td>
      <td>None</td>
      <td>5yrs</td>
      <td>[2006-01-01,2010-01-01)</td>
      <td>None</td>
      <td>20062010</td>
    </tr>
    <tr>
      <th>23</th>
      <td>None</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>acs</td>
      <td>None</td>
      <td>None</td>
      <td>carto-do-public-data.usa_carto.geography_usa_c...</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>carto-do-public-data.usa_acs.demographics_acs_...</td>
      <td>...</td>
      <td>eng</td>
      <td>American Community Survey (ACS) data at census...</td>
      <td>usa_acs</td>
      <td>USA American Community Survey</td>
      <td>od_acs_29664073</td>
      <td>None</td>
      <td>5yrs</td>
      <td>[2013-01-01,2018-01-01)</td>
      <td>None</td>
      <td>20132017</td>
    </tr>
    <tr>
      <th>27</th>
      <td>None</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>acs</td>
      <td>None</td>
      <td>None</td>
      <td>carto-do-public-data.tiger.geography_usa_cbsac...</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>carto-do-public-data.acs.demographics_acs_usa_...</td>
      <td>...</td>
      <td>eng</td>
      <td>American Community Survey (ACS) data at cbsacl...</td>
      <td>open_data</td>
      <td>Open Data</td>
      <td>od_acs_4bb9b377</td>
      <td>None</td>
      <td>5yrs</td>
      <td>[2010-01-01,2014-01-01)</td>
      <td>None</td>
      <td>20102014</td>
    </tr>
    <tr>
      <th>28</th>
      <td>None</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>acs</td>
      <td>None</td>
      <td>None</td>
      <td>carto-do-public-data.tiger.geography_usa_schoo...</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>carto-do-public-data.acs.demographics_acs_usa_...</td>
      <td>...</td>
      <td>eng</td>
      <td>American Community Survey (ACS) data at school...</td>
      <td>open_data</td>
      <td>Open Data</td>
      <td>od_acs_9df157a1</td>
      <td>None</td>
      <td>yearly</td>
      <td>[2014-01-01,2015-01-01)</td>
      <td>None</td>
      <td>2014</td>
    </tr>
    <tr>
      <th>29</th>
      <td>None</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>acs</td>
      <td>None</td>
      <td>None</td>
      <td>carto-do-public-data.tiger.geography_usa_count...</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>carto-do-public-data.acs.demographics_acs_usa_...</td>
      <td>...</td>
      <td>eng</td>
      <td>American Community Survey (ACS) data at county...</td>
      <td>open_data</td>
      <td>Open Data</td>
      <td>od_acs_550657ce</td>
      <td>None</td>
      <td>5yrs</td>
      <td>[2011-01-01,2015-01-01)</td>
      <td>None</td>
      <td>20112015</td>
    </tr>
    <tr>
      <th>31</th>
      <td>None</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>tiger</td>
      <td>None</td>
      <td>None</td>
      <td>carto-do-public-data.tiger.geography_usa_schoo...</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>carto-do-public-data.tiger.demographics_tiger_...</td>
      <td>...</td>
      <td>eng</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>open_data</td>
      <td>Open Data</td>
      <td>od_tiger_19a6dc83</td>
      <td>None</td>
      <td>yearly</td>
      <td>[2015-01-01,2016-01-01)</td>
      <td>None</td>
      <td>2015</td>
    </tr>
    <tr>
      <th>34</th>
      <td>None</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>acs</td>
      <td>None</td>
      <td>None</td>
      <td>carto-do-public-data.tiger.geography_usa_schoo...</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>carto-do-public-data.acs.demographics_acs_usa_...</td>
      <td>...</td>
      <td>eng</td>
      <td>American Community Survey (ACS) data at school...</td>
      <td>open_data</td>
      <td>Open Data</td>
      <td>od_acs_6e4b69f6</td>
      <td>None</td>
      <td>yearly</td>
      <td>[2014-01-01,2015-01-01)</td>
      <td>None</td>
      <td>2014</td>
    </tr>
    <tr>
      <th>39</th>
      <td>None</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>acs</td>
      <td>None</td>
      <td>None</td>
      <td>carto-do-public-data.tiger.geography_usa_place...</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>carto-do-public-data.acs.demographics_acs_usa_...</td>
      <td>...</td>
      <td>eng</td>
      <td>American Community Survey (ACS) data at placec...</td>
      <td>open_data</td>
      <td>Open Data</td>
      <td>od_acs_1a22afad</td>
      <td>None</td>
      <td>5yrs</td>
      <td>[2006-01-01,2010-01-01)</td>
      <td>None</td>
      <td>20062010</td>
    </tr>
    <tr>
      <th>52</th>
      <td>None</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>acs</td>
      <td>None</td>
      <td>None</td>
      <td>carto-do-public-data.tiger.geography_usa_cbsac...</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>carto-do-public-data.acs.demographics_acs_usa_...</td>
      <td>...</td>
      <td>eng</td>
      <td>American Community Survey (ACS) data at cbsacl...</td>
      <td>open_data</td>
      <td>Open Data</td>
      <td>od_acs_9510981d</td>
      <td>None</td>
      <td>5yrs</td>
      <td>[2013-01-01,2018-01-01)</td>
      <td>None</td>
      <td>20132017</td>
    </tr>
    <tr>
      <th>53</th>
      <td>None</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>acs</td>
      <td>None</td>
      <td>None</td>
      <td>carto-do-public-data.tiger.geography_usa_congr...</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>carto-do-public-data.acs.demographics_acs_usa_...</td>
      <td>...</td>
      <td>eng</td>
      <td>American Community Survey (ACS) data at congre...</td>
      <td>open_data</td>
      <td>Open Data</td>
      <td>od_acs_6d43ed82</td>
      <td>None</td>
      <td>5yrs</td>
      <td>[2013-01-01,2018-01-01)</td>
      <td>None</td>
      <td>20132017</td>
    </tr>
    <tr>
      <th>57</th>
      <td>None</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>acs</td>
      <td>None</td>
      <td>None</td>
      <td>carto-do-public-data.tiger.geography_usa_schoo...</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>carto-do-public-data.acs.demographics_acs_usa_...</td>
      <td>...</td>
      <td>eng</td>
      <td>American Community Survey (ACS) data at school...</td>
      <td>open_data</td>
      <td>Open Data</td>
      <td>od_acs_dc3cfd0f</td>
      <td>None</td>
      <td>5yrs</td>
      <td>[2006-01-01,2010-01-01)</td>
      <td>None</td>
      <td>20062010</td>
    </tr>
    <tr>
      <th>85</th>
      <td>None</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>acs</td>
      <td>None</td>
      <td>None</td>
      <td>carto-do-public-data.tiger.geography_usa_schoo...</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>carto-do-public-data.acs.demographics_acs_usa_...</td>
      <td>...</td>
      <td>eng</td>
      <td>American Community Survey (ACS) data at school...</td>
      <td>open_data</td>
      <td>Open Data</td>
      <td>od_acs_194c5960</td>
      <td>None</td>
      <td>yearly</td>
      <td>[2015-01-01,2016-01-01)</td>
      <td>None</td>
      <td>2015</td>
    </tr>
    <tr>
      <th>90</th>
      <td>None</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>acs</td>
      <td>None</td>
      <td>None</td>
      <td>carto-do-public-data.tiger.geography_usa_schoo...</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>carto-do-public-data.acs.demographics_acs_usa_...</td>
      <td>...</td>
      <td>eng</td>
      <td>American Community Survey (ACS) data at school...</td>
      <td>open_data</td>
      <td>Open Data</td>
      <td>od_acs_9a9c93b8</td>
      <td>None</td>
      <td>yearly</td>
      <td>[2010-01-01,2011-01-01)</td>
      <td>None</td>
      <td>2010</td>
    </tr>
    <tr>
      <th>91</th>
      <td>None</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>acs</td>
      <td>None</td>
      <td>None</td>
      <td>carto-do-public-data.tiger.geography_usa_schoo...</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>carto-do-public-data.acs.demographics_acs_usa_...</td>
      <td>...</td>
      <td>eng</td>
      <td>American Community Survey (ACS) data at school...</td>
      <td>open_data</td>
      <td>Open Data</td>
      <td>od_acs_7b2649a9</td>
      <td>None</td>
      <td>yearly</td>
      <td>[2010-01-01,2011-01-01)</td>
      <td>None</td>
      <td>2010</td>
    </tr>
    <tr>
      <th>92</th>
      <td>None</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>acs</td>
      <td>None</td>
      <td>None</td>
      <td>carto-do-public-data.tiger.geography_usa_cbsac...</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>carto-do-public-data.acs.demographics_acs_usa_...</td>
      <td>...</td>
      <td>eng</td>
      <td>American Community Survey (ACS) data at cbsacl...</td>
      <td>open_data</td>
      <td>Open Data</td>
      <td>od_acs_478c37b8</td>
      <td>None</td>
      <td>yearly</td>
      <td>[2017-01-01,2018-01-01)</td>
      <td>None</td>
      <td>2017</td>
    </tr>
    <tr>
      <th>93</th>
      <td>None</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>acs</td>
      <td>None</td>
      <td>None</td>
      <td>carto-do-public-data.tiger.geography_usa_congr...</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>carto-do-public-data.acs.demographics_acs_usa_...</td>
      <td>...</td>
      <td>eng</td>
      <td>American Community Survey (ACS) data at congre...</td>
      <td>open_data</td>
      <td>Open Data</td>
      <td>od_acs_f98ddfce</td>
      <td>None</td>
      <td>5yrs</td>
      <td>[2011-01-01,2015-01-01)</td>
      <td>None</td>
      <td>20112015</td>
    </tr>
    <tr>
      <th>96</th>
      <td>None</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>acs</td>
      <td>None</td>
      <td>None</td>
      <td>carto-do-public-data.tiger.geography_usa_pumac...</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>carto-do-public-data.acs.demographics_acs_usa_...</td>
      <td>...</td>
      <td>eng</td>
      <td>American Community Survey (ACS) data at pumacl...</td>
      <td>open_data</td>
      <td>Open Data</td>
      <td>od_acs_8b00f653</td>
      <td>None</td>
      <td>yearly</td>
      <td>[2014-01-01,2015-01-01)</td>
      <td>None</td>
      <td>2014</td>
    </tr>
    <tr>
      <th>97</th>
      <td>None</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>acs</td>
      <td>None</td>
      <td>None</td>
      <td>carto-do-public-data.tiger.geography_usa_schoo...</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>carto-do-public-data.acs.demographics_acs_usa_...</td>
      <td>...</td>
      <td>eng</td>
      <td>American Community Survey (ACS) data at school...</td>
      <td>open_data</td>
      <td>Open Data</td>
      <td>od_acs_d52a0635</td>
      <td>None</td>
      <td>5yrs</td>
      <td>[2011-01-01,2015-01-01)</td>
      <td>None</td>
      <td>20112015</td>
    </tr>
    <tr>
      <th>98</th>
      <td>None</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>acs</td>
      <td>None</td>
      <td>None</td>
      <td>carto-do-public-data.tiger.geography_usa_cbsac...</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>carto-do-public-data.acs.demographics_acs_usa_...</td>
      <td>...</td>
      <td>eng</td>
      <td>American Community Survey (ACS) data at cbsacl...</td>
      <td>open_data</td>
      <td>Open Data</td>
      <td>od_acs_1deaa51</td>
      <td>None</td>
      <td>5yrs</td>
      <td>[2011-01-01,2015-01-01)</td>
      <td>None</td>
      <td>20112015</td>
    </tr>
    <tr>
      <th>99</th>
      <td>None</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>acs</td>
      <td>None</td>
      <td>None</td>
      <td>carto-do-public-data.tiger.geography_usa_schoo...</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>carto-do-public-data.acs.demographics_acs_usa_...</td>
      <td>...</td>
      <td>eng</td>
      <td>American Community Survey (ACS) data at school...</td>
      <td>open_data</td>
      <td>Open Data</td>
      <td>od_acs_e0f5ff55</td>
      <td>None</td>
      <td>5yrs</td>
      <td>[2011-01-01,2015-01-01)</td>
      <td>None</td>
      <td>20112015</td>
    </tr>
    <tr>
      <th>100</th>
      <td>None</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>acs</td>
      <td>None</td>
      <td>None</td>
      <td>carto-do-public-data.tiger.geography_usa_pumac...</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>carto-do-public-data.acs.demographics_acs_usa_...</td>
      <td>...</td>
      <td>eng</td>
      <td>American Community Survey (ACS) data at pumacl...</td>
      <td>open_data</td>
      <td>Open Data</td>
      <td>od_acs_52710085</td>
      <td>None</td>
      <td>5yrs</td>
      <td>[2011-01-01,2015-01-01)</td>
      <td>None</td>
      <td>20112015</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>408</th>
      <td>None</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>tiger</td>
      <td>None</td>
      <td>None</td>
      <td>carto-do-public-data.tiger.geography_usa_censu...</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>carto-do-public-data.tiger.demographics_tiger_...</td>
      <td>...</td>
      <td>eng</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>open_data</td>
      <td>Open Data</td>
      <td>od_tiger_5e55275d</td>
      <td>None</td>
      <td>yearly</td>
      <td>[2015-01-01,2016-01-01)</td>
      <td>None</td>
      <td>2015</td>
    </tr>
    <tr>
      <th>409</th>
      <td>None</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>acs</td>
      <td>None</td>
      <td>None</td>
      <td>carto-do-public-data.tiger.geography_usa_place...</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>carto-do-public-data.acs.demographics_acs_usa_...</td>
      <td>...</td>
      <td>eng</td>
      <td>American Community Survey (ACS) data at placec...</td>
      <td>open_data</td>
      <td>Open Data</td>
      <td>od_acs_a665f9e1</td>
      <td>None</td>
      <td>yearly</td>
      <td>[2010-01-01,2011-01-01)</td>
      <td>None</td>
      <td>2010</td>
    </tr>
    <tr>
      <th>410</th>
      <td>None</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>acs</td>
      <td>None</td>
      <td>None</td>
      <td>carto-do-public-data.tiger.geography_usa_state...</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>carto-do-public-data.acs.demographics_acs_usa_...</td>
      <td>...</td>
      <td>eng</td>
      <td>American Community Survey (ACS) data at statec...</td>
      <td>open_data</td>
      <td>Open Data</td>
      <td>od_acs_5ec6965e</td>
      <td>None</td>
      <td>5yrs</td>
      <td>[2006-01-01,2010-01-01)</td>
      <td>None</td>
      <td>20062010</td>
    </tr>
    <tr>
      <th>411</th>
      <td>None</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>acs</td>
      <td>None</td>
      <td>None</td>
      <td>carto-do-public-data.tiger.geography_usa_congr...</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>carto-do-public-data.acs.demographics_acs_usa_...</td>
      <td>...</td>
      <td>eng</td>
      <td>American Community Survey (ACS) data at congre...</td>
      <td>open_data</td>
      <td>Open Data</td>
      <td>od_acs_f2f40516</td>
      <td>None</td>
      <td>yearly</td>
      <td>[2017-01-01,2018-01-01)</td>
      <td>None</td>
      <td>2017</td>
    </tr>
    <tr>
      <th>412</th>
      <td>None</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>acs</td>
      <td>None</td>
      <td>None</td>
      <td>carto-do-public-data.tiger.geography_usa_pumac...</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>carto-do-public-data.acs.demographics_acs_usa_...</td>
      <td>...</td>
      <td>eng</td>
      <td>American Community Survey (ACS) data at pumacl...</td>
      <td>open_data</td>
      <td>Open Data</td>
      <td>od_acs_1209a7e9</td>
      <td>None</td>
      <td>yearly</td>
      <td>[2017-01-01,2018-01-01)</td>
      <td>None</td>
      <td>2017</td>
    </tr>
    <tr>
      <th>413</th>
      <td>None</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>acs</td>
      <td>None</td>
      <td>None</td>
      <td>carto-do-public-data.tiger.geography_usa_congr...</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>carto-do-public-data.acs.demographics_acs_usa_...</td>
      <td>...</td>
      <td>eng</td>
      <td>American Community Survey (ACS) data at congre...</td>
      <td>open_data</td>
      <td>Open Data</td>
      <td>od_acs_6c9090b5</td>
      <td>None</td>
      <td>yearly</td>
      <td>[2010-01-01,2011-01-01)</td>
      <td>None</td>
      <td>2010</td>
    </tr>
    <tr>
      <th>414</th>
      <td>None</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>acs</td>
      <td>None</td>
      <td>None</td>
      <td>carto-do-public-data.tiger.geography_usa_state...</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>carto-do-public-data.acs.demographics_acs_usa_...</td>
      <td>...</td>
      <td>eng</td>
      <td>American Community Survey (ACS) data at statec...</td>
      <td>open_data</td>
      <td>Open Data</td>
      <td>od_acs_f9681e48</td>
      <td>None</td>
      <td>yearly</td>
      <td>[2017-01-01,2018-01-01)</td>
      <td>None</td>
      <td>2017</td>
    </tr>
    <tr>
      <th>415</th>
      <td>None</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>acs</td>
      <td>None</td>
      <td>None</td>
      <td>carto-do-public-data.tiger.geography_usa_cbsac...</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>carto-do-public-data.acs.demographics_acs_usa_...</td>
      <td>...</td>
      <td>eng</td>
      <td>American Community Survey (ACS) data at cbsacl...</td>
      <td>open_data</td>
      <td>Open Data</td>
      <td>od_acs_8c8516b</td>
      <td>None</td>
      <td>5yrs</td>
      <td>[2006-01-01,2010-01-01)</td>
      <td>None</td>
      <td>20062010</td>
    </tr>
    <tr>
      <th>416</th>
      <td>None</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>acs</td>
      <td>None</td>
      <td>None</td>
      <td>carto-do-public-data.tiger.geography_usa_place...</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>carto-do-public-data.acs.demographics_acs_usa_...</td>
      <td>...</td>
      <td>eng</td>
      <td>American Community Survey (ACS) data at placec...</td>
      <td>open_data</td>
      <td>Open Data</td>
      <td>od_acs_59534db1</td>
      <td>None</td>
      <td>5yrs</td>
      <td>[2010-01-01,2014-01-01)</td>
      <td>None</td>
      <td>20102014</td>
    </tr>
    <tr>
      <th>417</th>
      <td>None</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>acs</td>
      <td>None</td>
      <td>None</td>
      <td>carto-do-public-data.tiger.geography_usa_state...</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>carto-do-public-data.acs.demographics_acs_usa_...</td>
      <td>...</td>
      <td>eng</td>
      <td>American Community Survey (ACS) data at statec...</td>
      <td>open_data</td>
      <td>Open Data</td>
      <td>od_acs_57d06d64</td>
      <td>None</td>
      <td>5yrs</td>
      <td>[2011-01-01,2015-01-01)</td>
      <td>None</td>
      <td>20112015</td>
    </tr>
    <tr>
      <th>418</th>
      <td>None</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>acs</td>
      <td>None</td>
      <td>None</td>
      <td>carto-do-public-data.tiger.geography_usa_congr...</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>carto-do-public-data.acs.demographics_acs_usa_...</td>
      <td>...</td>
      <td>eng</td>
      <td>American Community Survey (ACS) data at congre...</td>
      <td>open_data</td>
      <td>Open Data</td>
      <td>od_acs_6bfd54ac</td>
      <td>None</td>
      <td>yearly</td>
      <td>[2014-01-01,2015-01-01)</td>
      <td>None</td>
      <td>2014</td>
    </tr>
    <tr>
      <th>419</th>
      <td>None</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>tiger</td>
      <td>None</td>
      <td>None</td>
      <td>carto-do-public-data.tiger.geography_usa_state...</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>carto-do-public-data.tiger.demographics_tiger_...</td>
      <td>...</td>
      <td>eng</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>open_data</td>
      <td>Open Data</td>
      <td>od_tiger_f9247903</td>
      <td>None</td>
      <td>yearly</td>
      <td>[2015-01-01,2016-01-01)</td>
      <td>None</td>
      <td>2015</td>
    </tr>
    <tr>
      <th>420</th>
      <td>None</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>acs</td>
      <td>None</td>
      <td>None</td>
      <td>carto-do-public-data.tiger.geography_usa_schoo...</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>carto-do-public-data.acs.demographics_acs_usa_...</td>
      <td>...</td>
      <td>eng</td>
      <td>American Community Survey (ACS) data at school...</td>
      <td>open_data</td>
      <td>Open Data</td>
      <td>od_acs_abd63a91</td>
      <td>None</td>
      <td>5yrs</td>
      <td>[2010-01-01,2014-01-01)</td>
      <td>None</td>
      <td>20102014</td>
    </tr>
    <tr>
      <th>422</th>
      <td>None</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>acs</td>
      <td>None</td>
      <td>None</td>
      <td>carto-do-public-data.tiger.geography_usa_schoo...</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>carto-do-public-data.acs.demographics_acs_usa_...</td>
      <td>...</td>
      <td>eng</td>
      <td>American Community Survey (ACS) data at school...</td>
      <td>open_data</td>
      <td>Open Data</td>
      <td>od_acs_e1b123b7</td>
      <td>None</td>
      <td>5yrs</td>
      <td>[2011-01-01,2015-01-01)</td>
      <td>None</td>
      <td>20112015</td>
    </tr>
    <tr>
      <th>423</th>
      <td>None</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>acs</td>
      <td>None</td>
      <td>None</td>
      <td>carto-do-public-data.tiger.geography_usa_state...</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>carto-do-public-data.acs.demographics_acs_usa_...</td>
      <td>...</td>
      <td>eng</td>
      <td>American Community Survey (ACS) data at statec...</td>
      <td>open_data</td>
      <td>Open Data</td>
      <td>od_acs_c31e5f28</td>
      <td>None</td>
      <td>5yrs</td>
      <td>[2013-01-01,2018-01-01)</td>
      <td>None</td>
      <td>20132017</td>
    </tr>
    <tr>
      <th>432</th>
      <td>None</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>tiger</td>
      <td>None</td>
      <td>None</td>
      <td>carto-do-public-data.tiger.geography_usa_block...</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>carto-do-public-data.tiger.demographics_tiger_...</td>
      <td>...</td>
      <td>eng</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>open_data</td>
      <td>Open Data</td>
      <td>od_tiger_476ce2e9</td>
      <td>None</td>
      <td>yearly</td>
      <td>[2015-01-01,2016-01-01)</td>
      <td>None</td>
      <td>2015</td>
    </tr>
    <tr>
      <th>433</th>
      <td>None</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>tiger</td>
      <td>None</td>
      <td>None</td>
      <td>carto-do-public-data.tiger.geography_usa_schoo...</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>carto-do-public-data.tiger.demographics_tiger_...</td>
      <td>...</td>
      <td>eng</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>open_data</td>
      <td>Open Data</td>
      <td>od_tiger_fac69779</td>
      <td>None</td>
      <td>yearly</td>
      <td>[2015-01-01,2016-01-01)</td>
      <td>None</td>
      <td>2015</td>
    </tr>
    <tr>
      <th>434</th>
      <td>None</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>tiger</td>
      <td>None</td>
      <td>None</td>
      <td>carto-do-public-data.tiger.geography_usa_place...</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>carto-do-public-data.tiger.demographics_tiger_...</td>
      <td>...</td>
      <td>eng</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>open_data</td>
      <td>Open Data</td>
      <td>od_tiger_384d0b09</td>
      <td>None</td>
      <td>yearly</td>
      <td>[2015-01-01,2016-01-01)</td>
      <td>None</td>
      <td>2015</td>
    </tr>
    <tr>
      <th>435</th>
      <td>None</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>acs</td>
      <td>None</td>
      <td>None</td>
      <td>carto-do-public-data.tiger.geography_usa_schoo...</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>carto-do-public-data.acs.demographics_acs_usa_...</td>
      <td>...</td>
      <td>eng</td>
      <td>American Community Survey (ACS) data at school...</td>
      <td>open_data</td>
      <td>Open Data</td>
      <td>od_acs_7c4b8db0</td>
      <td>None</td>
      <td>yearly</td>
      <td>[2014-01-01,2015-01-01)</td>
      <td>None</td>
      <td>2014</td>
    </tr>
    <tr>
      <th>436</th>
      <td>None</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>acs</td>
      <td>None</td>
      <td>None</td>
      <td>carto-do-public-data.tiger.geography_usa_schoo...</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>carto-do-public-data.acs.demographics_acs_usa_...</td>
      <td>...</td>
      <td>eng</td>
      <td>American Community Survey (ACS) data at school...</td>
      <td>open_data</td>
      <td>Open Data</td>
      <td>od_acs_eaf66737</td>
      <td>None</td>
      <td>yearly</td>
      <td>[2015-01-01,2016-01-01)</td>
      <td>None</td>
      <td>2015</td>
    </tr>
    <tr>
      <th>437</th>
      <td>None</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>lodes</td>
      <td>None</td>
      <td>None</td>
      <td>carto-do-public-data.tiger.geography_usa_block...</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>carto-do-public-data.lodes.demographics_lodes_...</td>
      <td>...</td>
      <td>eng</td>
      <td>LEHD Origin-Destination Employment Statistics ...</td>
      <td>open_data</td>
      <td>Open Data</td>
      <td>od_lodes_b4b9dfac</td>
      <td>None</td>
      <td>yearly</td>
      <td>[2013-01-01,2014-01-01)</td>
      <td>None</td>
      <td>2013</td>
    </tr>
    <tr>
      <th>438</th>
      <td>None</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>acs</td>
      <td>None</td>
      <td>None</td>
      <td>carto-do-public-data.tiger.geography_usa_state...</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>carto-do-public-data.acs.demographics_acs_usa_...</td>
      <td>...</td>
      <td>eng</td>
      <td>American Community Survey (ACS) data at statec...</td>
      <td>open_data</td>
      <td>Open Data</td>
      <td>od_acs_17667f64</td>
      <td>None</td>
      <td>yearly</td>
      <td>[2015-01-01,2016-01-01)</td>
      <td>None</td>
      <td>2015</td>
    </tr>
    <tr>
      <th>439</th>
      <td>None</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>acs</td>
      <td>None</td>
      <td>None</td>
      <td>carto-do-public-data.tiger.geography_usa_pumac...</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>carto-do-public-data.acs.demographics_acs_usa_...</td>
      <td>...</td>
      <td>eng</td>
      <td>American Community Survey (ACS) data at pumacl...</td>
      <td>open_data</td>
      <td>Open Data</td>
      <td>od_acs_8c6d324a</td>
      <td>None</td>
      <td>yearly</td>
      <td>[2010-01-01,2011-01-01)</td>
      <td>None</td>
      <td>2010</td>
    </tr>
    <tr>
      <th>440</th>
      <td>None</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>acs</td>
      <td>None</td>
      <td>None</td>
      <td>carto-do-public-data.tiger.geography_usa_place...</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>carto-do-public-data.acs.demographics_acs_usa_...</td>
      <td>...</td>
      <td>eng</td>
      <td>American Community Survey (ACS) data at placec...</td>
      <td>open_data</td>
      <td>Open Data</td>
      <td>od_acs_d60f0d6e</td>
      <td>None</td>
      <td>yearly</td>
      <td>[2015-01-01,2016-01-01)</td>
      <td>None</td>
      <td>2015</td>
    </tr>
    <tr>
      <th>441</th>
      <td>None</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>tiger</td>
      <td>None</td>
      <td>None</td>
      <td>carto-do-public-data.tiger.geography_usa_congr...</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>carto-do-public-data.tiger.demographics_tiger_...</td>
      <td>...</td>
      <td>eng</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>open_data</td>
      <td>Open Data</td>
      <td>od_tiger_e10059f</td>
      <td>None</td>
      <td>yearly</td>
      <td>[2015-01-01,2016-01-01)</td>
      <td>None</td>
      <td>2015</td>
    </tr>
    <tr>
      <th>442</th>
      <td>None</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>acs</td>
      <td>None</td>
      <td>None</td>
      <td>carto-do-public-data.tiger.geography_usa_block...</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>carto-do-public-data.acs.demographics_acs_usa_...</td>
      <td>...</td>
      <td>eng</td>
      <td>American Community Survey (ACS) data at blockg...</td>
      <td>open_data</td>
      <td>Open Data</td>
      <td>od_acs_4f56aa89</td>
      <td>None</td>
      <td>5yrs</td>
      <td>[2013-01-01,2018-01-01)</td>
      <td>None</td>
      <td>20132017</td>
    </tr>
    <tr>
      <th>443</th>
      <td>None</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>acs</td>
      <td>None</td>
      <td>None</td>
      <td>carto-do-public-data.tiger.geography_usa_cbsac...</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>carto-do-public-data.acs.demographics_acs_usa_...</td>
      <td>...</td>
      <td>eng</td>
      <td>American Community Survey (ACS) data at cbsacl...</td>
      <td>open_data</td>
      <td>Open Data</td>
      <td>od_acs_d9e8a21b</td>
      <td>None</td>
      <td>yearly</td>
      <td>[2010-01-01,2011-01-01)</td>
      <td>None</td>
      <td>2010</td>
    </tr>
    <tr>
      <th>448</th>
      <td>None</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>acs</td>
      <td>None</td>
      <td>None</td>
      <td>carto-do-public-data.tiger.geography_usa_count...</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>carto-do-public-data.acs.demographics_acs_usa_...</td>
      <td>...</td>
      <td>eng</td>
      <td>American Community Survey (ACS) data at county...</td>
      <td>open_data</td>
      <td>Open Data</td>
      <td>od_acs_c5eb4b5e</td>
      <td>None</td>
      <td>yearly</td>
      <td>[2010-01-01,2011-01-01)</td>
      <td>None</td>
      <td>2010</td>
    </tr>
    <tr>
      <th>450</th>
      <td>None</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>acs</td>
      <td>None</td>
      <td>None</td>
      <td>carto-do-public-data.tiger.geography_usa_cbsac...</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>carto-do-public-data.acs.demographics_acs_usa_...</td>
      <td>...</td>
      <td>eng</td>
      <td>American Community Survey (ACS) data at cbsacl...</td>
      <td>open_data</td>
      <td>Open Data</td>
      <td>od_acs_de856602</td>
      <td>None</td>
      <td>yearly</td>
      <td>[2014-01-01,2015-01-01)</td>
      <td>None</td>
      <td>2014</td>
    </tr>
    <tr>
      <th>451</th>
      <td>None</td>
      <td>demographics</td>
      <td>Demographics</td>
      <td>usa</td>
      <td>acs</td>
      <td>None</td>
      <td>None</td>
      <td>carto-do-public-data.tiger.geography_usa_censu...</td>
      <td>Topologically Integrated Geographic Encoding a...</td>
      <td>carto-do-public-data.acs.demographics_acs_usa_...</td>
      <td>...</td>
      <td>eng</td>
      <td>American Community Survey (ACS) data at census...</td>
      <td>open_data</td>
      <td>Open Data</td>
      <td>od_acs_5978c550</td>
      <td>None</td>
      <td>5yrs</td>
      <td>[2006-01-01,2010-01-01)</td>
      <td>None</td>
      <td>20062010</td>
    </tr>
  </tbody>
</table>
<p>92 rows × 21 columns</p>
</div>

### Conclusion

In this guide we've presented how to explore the Data Observatory catalog on the seek for variables of datasets that we can use to enrich our own data.

We've learnt:

- How to discover the catalog using nested hierarchical filters.
- Describe the three main entities in the catalog: `Geography`, `Dataset` and their `Variables`
- Get a glimpse of the data and stats taken from the actual repository, for a better informed decision on what variables choose.
- Subscribe to the choosen datasets to get a license that grants the right to enrich your own data.

We recommend you to check also these resources if you want to know more about the Data Observatory catalog:

- The CARTOframes [enrichment guide](/developers/developers/cartoframes/guides/Data-enrichment/)
- [Our public website](/platform/location-data-streams/)
- Your user dashboard: Under the data section
- The CARTOframes catalog [API reference](/developers/cartoframes/reference/#heading-Data-Observatory)
