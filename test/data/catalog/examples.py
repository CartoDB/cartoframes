from cartoframes.data.catalog.variable import Variable, Variables
from cartoframes.data.catalog.dataset import Dataset, Datasets
from cartoframes.data.catalog.category import Category, Categories
from cartoframes.data.catalog.geography import Geography, Geographies
from cartoframes.data.catalog.country import Country, Countries

test_country1 = Country({'iso_code3': 'esp'})
test_country2 = Country({'iso_code3': 'usa'})
test_countries = Countries([test_country1, test_country2])

test_category1 = Category({
    'id': 'cat1',
    'name': 'Financial'
})
test_category2 = Category({
    'id': 'cat2',
    'name': 'Demographics'
})
test_categories = Categories([test_category1, test_category2])

test_geography1 = Geography({
    'id': 'carto-do-public-data.tiger.geography_esp_census_2019',
    'name': 'ESP - Census',
    'provider_id': 'bbva',
    'country_iso_code3': 'esp',
    'version': '20190203',
    'is_public': True
})
test_geography2 = Geography({
    'id': 'carto-do-public-data.tiger.geography_esp_municipalities_2019',
    'name': 'ESP - Municipalities',
    'provider_id': 'bbva',
    'country_iso_code3': 'esp',
    'version': '20190203',
    'is_public': False
})
test_geographies = Geographies([test_geography1, test_geography2])

test_dataset1 = Dataset({
    'id': 'basicstats-census',
    'name': 'Basic Stats - Census',
    'provider_id': 'bbva',
    'category_id': 'demographics',
    'country_iso_code3': 'esp',
    'geography_id': 'carto-do-public-data.tiger.geography_esp_census_2019',
    'temporal_aggregations': '5yrs',
    'time_coverage': ['2006-01-01', '2010-01-01'],
    'group_id': 'basicstats_esp_2019',
    'version': '20190203',
    'is_public': True
})
test_dataset2 = Dataset({
    'id': 'basicstats-municipalities',
    'name': 'Basic Stats - Municipalities',
    'provider_id': 'bbva',
    'category_id': 'demographics',
    'country_iso_code3': 'esp',
    'geography_id': 'carto-do-public-data.tiger.geography_esp_municipalities_2019',
    'temporal_aggregations': '5yrs',
    'time_coverage': ['2006-01-01', '2010-01-01'],
    'group_id': 'basicstats_esp_2019',
    'version': '20190203',
    'is_public': False
})
test_datasets = Datasets([test_dataset1, test_dataset2])

test_variable1 = Variable({
    'id': 'var1',
    'name': 'Population',
    'group_id': 'vargroup1'
})
test_variable2 = Variable({
    'id': 'var2',
    'name': 'Date',
    'group_id': 'vargroup1'
})
test_variables = Variables([test_variable1, test_variable2])
