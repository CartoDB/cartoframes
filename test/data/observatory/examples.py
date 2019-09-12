from cartoframes.data.observatory.variable import Variable, Variables
from cartoframes.data.observatory.dataset import Dataset, Datasets
from cartoframes.data.observatory.category import Category, Categories
from cartoframes.data.observatory.geography import Geography, Geographies
from cartoframes.data.observatory.country import Country, Countries
from cartoframes.data.observatory.provider import Provider, Providers

db_country1 = {'country_iso_code3': 'esp'}
db_country2 = {'country_iso_code3': 'usa'}
test_country1 = Country(db_country1)
test_country2 = Country(db_country2)
test_countries = Countries([test_country1, test_country2])

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
test_categories = Categories([test_category1, test_category2])

db_geography1 = {
    'id': 'carto-do-public-data.tiger.geography_esp_census_2019',
    'name': 'ESP - Census',
    'provider_id': 'bbva',
    'country_iso_code3': 'esp',
    'version': '20190203',
    'is_public_data': True
}
db_geography2 = {
    'id': 'carto-do-public-data.tiger.geography_esp_municipalities_2019',
    'name': 'ESP - Municipalities',
    'provider_id': 'bbva',
    'country_iso_code3': 'esp',
    'version': '20190203',
    'is_public_data': False
}
test_geography1 = Geography(db_geography1)
test_geography2 = Geography(db_geography2)
test_geographies = Geographies([test_geography1, test_geography2])

db_dataset1 = {
    'id': 'basicstats-census',
    'name': 'Basic Stats - Census',
    'provider_id': 'bbva',
    'category_id': 'demographics',
    'country_iso_code3': 'esp',
    'geography_id': 'carto-do-public-data.tiger.geography_esp_census_2019',
    'temporalaggregations': '5yrs',
    'time_coverage': ['2006-01-01', '2010-01-01'],
    'datasets_groups_id': 'basicstats_esp_2019',
    'version': '20190203',
    'is_public_data': True,
    'subscription_list_price': '',
    'subscription_tos': '',
    'is_sample': False
}
db_dataset2 = {
    'id': 'basicstats-municipalities',
    'name': 'Basic Stats - Municipalities',
    'provider_id': 'bbva',
    'category_id': 'demographics',
    'country_iso_code3': 'esp',
    'geography_id': 'carto-do-public-data.tiger.geography_esp_municipalities_2019',
    'temporalaggregations': '5yrs',
    'time_coverage': ['2006-01-01', '2010-01-01'],
    'datasets_groups_id': 'basicstats_esp_2019',
    'version': '20190203',
    'is_public_data': False,
    'subscription_list_price': '',
    'subscription_tos': '',
    'is_sample': False
}
test_dataset1 = Dataset(db_dataset1)
test_dataset2 = Dataset(db_dataset2)
test_datasets = Datasets([test_dataset1, test_dataset2])

db_variable1 = {
    'id': 'var1',
    'name': 'Population',
    'variable_group_id': 'vargroup1',
    'description': 'The number of people within each geography',
    'column_name': 'pop',
    'db_type': 'Numeric',
    'group_id': 'vargroup1',
    'agg_method': '',
    'starred': True
}
db_variable2 = {
    'id': 'var2',
    'name': 'Date',
    'variable_group_id': 'vargroup1',
    'description': 'The date the data refers to (YYYY-MM format for month and YYYY-MM-DD for day).',
    'column_name': 'Date',
    'db_type': 'STRING',
    'group_id': 'vargroup1',
    'agg_method': '',
    'starred': False
}
test_variable1 = Variable(db_variable1)
test_variable2 = Variable(db_variable2)
test_variables = Variables([test_variable1, test_variable2])

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
test_providers = Providers([test_provider1, test_provider2])
