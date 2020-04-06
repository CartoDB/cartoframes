import pandas as pd

from unittest.mock import patch

from cartoframes.data.observatory.catalog.entity import CatalogList
from cartoframes.data.observatory.catalog.variable import Variable
from cartoframes.data.observatory.catalog.repository.variable_repo import VariableRepository
from cartoframes.data.observatory.catalog.repository.dataset_repo import DatasetRepository
from cartoframes.data.observatory.catalog.repository.constants import VARIABLE_FILTER
from .examples import test_datasets, test_variable1, test_variables, db_variable1, test_variable2, db_variable2


class TestVariable(object):

    @patch.object(VariableRepository, 'get_by_id')
    def test_get_variable_by_id(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_variable1

        # When
        variable = Variable.get(test_variable1.id)

        # Then
        assert isinstance(variable, object)
        assert isinstance(variable, Variable)
        assert variable == test_variable1

    @patch.object(DatasetRepository, 'get_all')
    def test_get_datasets_by_variable(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_datasets

        # When
        datasets = test_variable1.datasets

        # Then
        mocked_repo.assert_called_once_with({VARIABLE_FILTER: test_variable1.id})
        assert isinstance(datasets, list)
        assert isinstance(datasets, CatalogList)
        assert datasets == test_datasets

    def test_variable_properties(self):
        # Given
        variable = Variable(db_variable1)

        # When
        variable_id = variable.id
        slug = variable.slug
        name = variable.name
        description = variable.description
        column_name = variable.column_name
        db_type = variable.db_type
        dataset = variable.dataset
        agg_method = variable.agg_method
        variable_group = variable.variable_group
        summary = variable.summary

        # Then
        assert variable_id == db_variable1['id']
        assert slug == db_variable1['slug']
        assert name == db_variable1['name']
        assert description == db_variable1['description']
        assert column_name == db_variable1['column_name']
        assert db_type == db_variable1['db_type']
        assert dataset == db_variable1['dataset_id']
        assert agg_method == db_variable1['agg_method']
        assert variable_group == db_variable1['variable_group_id']
        assert summary == db_variable1['summary_json']

    def test_variable_is_exported_as_series(self):
        # Given
        variable = test_variable1

        # When
        variable_series = variable.to_series()

        # Then
        assert isinstance(variable_series, pd.Series)
        assert variable_series['id'] == variable.id

    def test_variable_is_exported_as_dict(self):
        # Given
        variable = Variable(db_variable1)
        expected_dict = {key: value for key, value in db_variable1.items() if key != 'summary_json'}

        # When
        variable_dict = variable.to_dict()

        # Then
        assert isinstance(variable_dict, dict)
        assert variable_dict == expected_dict

    def test_variable_is_represented_with_slug_and_description(self):
        # Given
        variable = Variable(db_variable1)

        # When
        variable_repr = repr(variable)

        # Then
        assert variable_repr == "<Variable.get('{slug}')> #'{descr}'"\
                                .format(slug=db_variable1['slug'], descr=db_variable1['description'])

    def test_variable_is_printed_with_classname(self):
        # Given
        variable = Variable(db_variable1)

        # When
        variable_str = str(variable)

        # Then
        assert variable_str == 'Variable({dict_str})'.format(dict_str=str(db_variable1))

    @patch.object(VariableRepository, 'get_all')
    def test_get_all_variables(self, mocked_repo):
        # Given
        mocked_repo.return_value = test_variables

        # When
        variables = Variable.get_all()

        # Then
        assert isinstance(variables, list)
        assert isinstance(variables, CatalogList)
        assert variables == test_variables

    def test_variable_list_is_printed_correctly(self):
        # Given
        variables = CatalogList([test_variable1, test_variable2])
        shorten_description = test_variable2.description[0:50] + '...'

        # When
        variables_str = str(variables)

        # Then
        assert variables_str == "[<Variable.get('{id1}')> #'{descr1}', <Variable.get('{id2}')> #'{descr2}']" \
                                .format(id1=db_variable1['slug'], descr1=db_variable1['description'],
                                        id2=db_variable2['slug'], descr2=shorten_description)

    def test_variable_list_is_represented_correctly(self):
        # Given
        variables = CatalogList([test_variable1, test_variable2])
        shorten_description = test_variable2.description[0:50] + '...'

        # When
        variables_repr = repr(variables)

        # Then
        assert variables_repr == "[<Variable.get('{id1}')> #'{descr1}', <Variable.get('{id2}')> #'{descr2}']" \
                                 .format(id1=db_variable1['slug'], descr1=db_variable1['description'],
                                         id2=db_variable2['slug'], descr2=shorten_description)

    def test_variables_items_are_obtained_as_variable(self):
        # Given
        variables = test_variables

        # When
        variable = variables[0]

        # Then
        assert isinstance(variable, Variable)
        assert variable == test_variable1

    def test_variables_are_exported_as_dataframe(self):
        # Given
        variables = test_variables
        variable = variables[0]
        expected_variable_df = variable.to_series()
        del expected_variable_df['summary_json']

        # When
        variable_df = variables.to_dataframe()
        sliced_variable = variable_df.iloc[0]

        # Then
        assert isinstance(variable_df, pd.DataFrame)
        assert isinstance(sliced_variable, pd.Series)
        assert sliced_variable.equals(expected_variable_df)
