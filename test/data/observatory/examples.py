from cartoframes.data.observatory.variable import Variable, Variables
from cartoframes.data.observatory.dataset import Dataset, Datasets
from cartoframes.data.observatory.category import Category, Categories
from cartoframes.data.observatory.geography import Geography, Geographies
from cartoframes.data.observatory.country import Country, Countries

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
    'is_public_data': True
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
    'is_public_data': False
}
test_dataset1 = Dataset(db_dataset1)
test_dataset2 = Dataset(db_dataset2)
test_datasets = Datasets([test_dataset1, test_dataset2])

db_variable1 = {
    'id': 'var1',
    'name': 'Population',
    'variable_group_id': 'vargroup1'
}
db_variable2 = {
    'id': 'var2',
    'name': 'Date',
    'variable_group_id': 'vargroup1'
}
test_variable1 = Variable(db_variable1)
test_variable2 = Variable(db_variable2)
test_variables = Variables([test_variable1, test_variable2])
