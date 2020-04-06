from cartoframes.data.observatory.catalog.variable import Variable
from cartoframes.data.observatory.catalog.dataset import Dataset
from cartoframes.data.observatory.catalog.category import Category
from cartoframes.data.observatory.catalog.geography import Geography
from cartoframes.data.observatory.catalog.country import Country
from cartoframes.data.observatory.catalog.provider import Provider
from cartoframes.data.observatory.catalog.variable_group import VariableGroup
from cartoframes.data.observatory.catalog.entity import CatalogList

db_country1 = {'id': 'esp', 'name': 'Spain'}
db_country2 = {'id': 'usa', 'name': 'United States of America'}
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
    'provider_name': 'bbva',
    'country_id': 'esp',
    'lang': 'esp',
    'geom_coverage': '',
    'geom_type': '',
    'update_frequency': 'monthly',
    'version': '20190203',
    'is_public_data': True,
    'summary_json': {}
}
db_geography2 = {
    'id': 'carto-do-public.tiger.geography_esp_municipalities_2019',
    'slug': 'esp_municipalities_2019_3456789c',
    'name': 'ESP - Municipalities',
    'description': 'Geography data for Spanish municipalities',
    'provider_id': 'bbva',
    'provider_name': 'bbva',
    'country_id': 'esp',
    'lang': 'esp',
    'geom_coverage': '',
    'geom_type': '',
    'update_frequency': 'monthly',
    'version': '20190203',
    'is_public_data': False,
    'summary_json': {}
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
    'provider_name': 'bbva',
    'category_id': 'demographics',
    'category_name': 'demographics',
    'data_source_id': 'basicstats',
    'country_id': 'esp',
    'lang': 'esp',
    'geography_id': 'carto-do-public-data.tiger.geography_esp_census_2019',
    'geography_name': 'Tiger municipalities from Spain',
    'geography_description': 'Points',
    'temporal_aggregation': '5yrs',
    'time_coverage': ['2006-01-01', '2010-01-01'],
    'update_frequency': 'monthly',
    'version': '20190203',
    'is_public_data': True,
    'summary_json': None
}
db_dataset2 = {
    'id': 'carto-do-public.project.basicstats-municipalities',
    'slug': 'basicstats_municipalities_2345678b',
    'name': 'Basic Stats - Municipalities',
    'description': 'Basic stats on 2019 Spanish municipalities',
    'provider_id': 'bbva',
    'provider_name': 'bbva',
    'category_id': 'demographics',
    'category_name': 'demographics',
    'data_source_id': 'basicstats',
    'country_id': 'esp',
    'lang': 'esp',
    'geography_id': 'carto-do-public-data.tiger.geography_esp_municipalities_2019',
    'geography_name': 'Tiger municipalities from Spain',
    'geography_description': 'Points',
    'temporal_aggregation': '5yrs',
    'time_coverage': ['2006-01-01', '2010-01-01'],
    'update_frequency': 'monthly',
    'version': '20190203',
    'is_public_data': False,
    'summary_json': {
        'glimpses': {
            'head': ['a', 'b', 'c'],
            'tail': ['e', 'f', 'g']
        },
        'counts': {
            'rows': 3,
            'columns': 3,
            'null_cells': 0,
            'null_cells_percent': 0
        },
        'fields_by_type': {
            'float': 1,
            'string': 1,
            'integer': 1
        }
    }
}
test_dataset1 = Dataset(db_dataset1)
test_dataset2 = Dataset(db_dataset2)
test_datasets = CatalogList([test_dataset1, test_dataset2])

db_variable1 = {
    'id': 'carto-do.variable.var1',
    'slug': 'var1',
    'name': 'Population',
    'description': 'Number of people',
    'column_name': 'pop',
    'db_type': 'Numeric',
    'dataset_id': 'dataset1',
    'agg_method': '',
    'variable_group_id': 'vargroup1',
    'summary_json': None
}
db_variable2 = {
    'id': 'carto-do.variable.var2',
    'slug': 'var2',
    'name': 'Date',
    'description': 'The date the data refers to (YYYY-MM format for month and YYYY-MM-DD for day).',
    'column_name': 'Date',
    'db_type': 'STRING',
    'dataset_id': 'dataset1',
    'agg_method': '',
    'variable_group_id': 'vargroup1',
    'summary_json': [{'key': 'value'}]
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
    'id': 'carto-do.variable_group.vargroup1',
    'slug': 'vargroup1',
    'name': 'Population',
    'dataset_id': 'dataset1'
}
db_variable_group2 = {
    'id': 'carto-do.variable_group.vargroup2',
    'slug': 'vargroup2',
    'name': 'Date',
    'dataset_id': 'dataset1'
}
test_variable_group1 = VariableGroup(db_variable_group1)
test_variable_group2 = VariableGroup(db_variable_group2)
test_variables_groups = CatalogList([test_variable_group1, test_variable_group2])

test_subscription_info = {
    'id': 'id',
    'estimated_delivery_days': 0,
    'subscription_list_price': 100,
    'tos': 'tos',
    'tos_link': 'tos_link',
    'licenses': 'licenses',
    'licenses_link': 'licenses_link',
    'rights': 'rights'
}
