from cartoframes.data.observatory.variable import Variable
from cartoframes.data.observatory.dataset import Dataset
from cartoframes.data.observatory.category import Category
from cartoframes.data.observatory.geography import Geography
from cartoframes.data.observatory.country import Country
from cartoframes.data.observatory.provider import Provider
from cartoframes.data.observatory.variable_group import VariableGroup
from cartoframes.data.observatory.entity import CatalogList

db_country1 = {'id': 'esp'}
db_country2 = {'id': 'usa'}
test_country1 = Country(db_country1)
test_country2 = Country(db_country2)
test_countries = CatalogList([test_country1, test_country2])

db_category1 = {
    'id': 'cat1',
    'name': 'Financial'
}
db_category2 = {
    'id': 'cat2',
    'name': 'Demographics'
}
test_category1 = Category(db_category1)
test_category2 = Category(db_category2)
test_categories = CatalogList([test_category1, test_category2])

db_geography1 = {
    'id': 'carto-do-public.tiger.geography_esp_census_2019',
    'slug': 'esp_census_2019_4567890d',
    'name': 'ESP - Census',
    'description': 'Geography data for Spanish census',
    'provider_id': 'bbva',
    'country_id': 'esp',
    'lang': 'esp',
    'geom_coverage': '',
    'update_frequency': 'monthly',
    'version': '20190203',
    'is_public_data': True,
    'summary_jsonb': {}
}
db_geography2 = {
    'id': 'carto-do-public.tiger.geography_esp_municipalities_2019',
    'slug': 'esp_municipalities_2019_3456789c',
    'name': 'ESP - Municipalities',
    'description': 'Geography data for Spanish municipalities',
    'provider_id': 'bbva',
    'country_id': 'esp',
    'lang': 'esp',
    'geom_coverage': '',
    'update_frequency': 'monthly',
    'version': '20190203',
    'is_public_data': False,
    'summary_jsonb': {}
}
test_geography1 = Geography(db_geography1)
test_geography2 = Geography(db_geography2)
test_geographies = CatalogList([test_geography1, test_geography2])

db_dataset1 = {
    'id': 'carto-do-public.project.basicstats-census',
    'slug': 'basicstats_census_1234567a',
    'name': 'Basic Stats - Census',
    'description': 'Basic stats on 2019 Spanish census',
    'provider_id': 'bbva',
    'category_id': 'demographics',
    'data_source_id': 'basicstats',
    'country_id': 'esp',
    'lang': 'esp',
    'geography_id': 'carto-do-public-data.tiger.geography_esp_census_2019',
    'temporal_aggregation': '5yrs',
    'time_coverage': ['2006-01-01', '2010-01-01'],
    'update_frequency': 'monthly',
    'version': '20190203',
    'is_public_data': True,
    'summary_jsonb': {}
}
db_dataset2 = {
    'id': 'carto-do-public.project.basicstats-municipalities',
    'slug': 'basicstats_municipalities_2345678b',
    'name': 'Basic Stats - Municipalities',
    'description': 'Basic stats on 2019 Spanish municipalities',
    'provider_id': 'bbva',
    'category_id': 'demographics',
    'data_source_id': 'basicstats',
    'country_id': 'esp',
    'lang': 'esp',
    'geography_id': 'carto-do-public-data.tiger.geography_esp_municipalities_2019',
    'temporal_aggregation': '5yrs',
    'time_coverage': ['2006-01-01', '2010-01-01'],
    'update_frequency': 'monthly',
    'version': '20190203',
    'is_public_data': False,
    'summary_jsonb': {}
}
test_dataset1 = Dataset(db_dataset1)
test_dataset2 = Dataset(db_dataset2)
test_datasets = CatalogList([test_dataset1, test_dataset2])

db_variable1 = {
    'id': 'var1',
    'name': 'Population',
    'description': 'The number of people within each geography',
    'column_name': 'pop',
    'db_type': 'Numeric',
    'dataset_id': 'dataset1',
    'agg_method': '',
    'variable_group_id': 'vargroup1',
    'starred': True,
    'summary_jsonb': {}
}
db_variable2 = {
    'id': 'var2',
    'name': 'Date',
    'description': 'The date the data refers to (YYYY-MM format for month and YYYY-MM-DD for day).',
    'column_name': 'Date',
    'db_type': 'STRING',
    'dataset_id': 'dataset1',
    'agg_method': '',
    'variable_group_id': 'vargroup1',
    'starred': False,
    'summary_jsonb': {}
}
test_variable1 = Variable(db_variable1)
test_variable2 = Variable(db_variable2)
test_variables = CatalogList([test_variable1, test_variable2])

db_provider1 = {
    'id': 'bbva',
    'name': 'BBVA'
}
db_provider2 = {
    'id': 'open_data',
    'name': 'Open Data'
}
test_provider1 = Provider(db_provider1)
test_provider2 = Provider(db_provider2)
test_providers = CatalogList([test_provider1, test_provider2])

db_variable_group1 = {
    'id': 'vargroup1',
    'name': 'Population',
    'dataset_id': 'dataset1',
    'starred': True
}
db_variable_group2 = {
    'id': 'vargroup2',
    'name': 'Date',
    'dataset_id': 'dataset1',
    'starred': False
}
test_variable_group1 = VariableGroup(db_variable_group1)
test_variable_group2 = VariableGroup(db_variable_group2)
test_variables_groups = CatalogList([test_variable_group1, test_variable_group2])
