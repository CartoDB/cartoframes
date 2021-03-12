import pandas as pd

from .entity import CatalogEntity
from .repository.dataset_repo import get_dataset_repo
from .repository.variable_repo import get_variable_repo
from .repository.constants import VARIABLE_FILTER
from .summary import variable_describe, head, tail, counts, quantiles, top_values, histogram


_DESCRIPTION_LENGTH_LIMIT = 50


class Variable(CatalogEntity):
    """This class represents a :py:class:`Variable <cartoframes.data.observatory.Variable>`
    of datasets in the :py:class:`Catalog <cartoframes.data.observatory.Catalog>`.

    Variables contain column names, description, data type, aggregation method, and some other metadata that is
    useful to understand the underlying data inside a :obj:`Dataset`

    Examples:
        List the variables of a :py:class:`Dataset <cartoframes.data.observatory.Dataset>`
        in combination with nested filters (categories, countries, etc.)

        >>> dataset = Dataset.get('mbi_retail_turn_705247a')
        >>> dataset.variables
        [<Variable.get('RT_CI_95050c10')> #'Retail Turnover: index (country eq.100)', ...]

    """
    _entity_repo = get_variable_repo()

    @property
    def datasets(self):
        """Get the list of datasets related to this variable.

        Returns:
            :py:class:`CatalogList <cartoframes.data.observatory.entity.CatalogList>` List of Dataset instances.

        Raises:
            CatalogError: if there's a problem when connecting to the catalog or no datasets are found.

        """
        return get_dataset_repo().get_all({VARIABLE_FILTER: self.id})

    @property
    def name(self):
        """Name of this variable."""
        return self.data['name']

    @property
    def description(self):
        """Description of this variable."""
        return self.data['description']

    @property
    def column_name(self):
        """Column name of the actual table related to the variable in the :obj:`Dataset`."""
        return self.data['column_name']

    @property
    def db_type(self):
        """Type in the database.

        Returns:
            str

        Examples: INTEGER, STRING, FLOAT, GEOGRAPHY, JSON, BOOL, etc.

        """
        return self.data['db_type']

    @property
    def dataset(self):
        """ID of the :obj:`Dataset` to which this variable belongs."""
        return self.data['dataset_id']

    @property
    def agg_method(self):
        """Text representing a description of the aggregation method used to compute the values in this `Variable`"""
        return self.data['agg_method']

    @property
    def variable_group(self):
        """If any, ID of the variable group to which this variable belongs."""
        return self.data['variable_group_id']

    @property
    def summary(self):
        """JSON object with extra metadata that summarizes different properties of this variable."""
        return self.data['summary_json']

    @property
    def project_name(self):
        project, _, _, _ = self.id.split('.')
        return project

    @property
    def schema_name(self):
        _, schema, _, _ = self.id.split('.')
        return schema

    @property
    def dataset_name(self):
        _, _, dataset, _ = self.id.split('.')
        return dataset

    def describe(self, autoformat=True):
        """Shows a summary of the actual stats of the variable (column) of the dataset.
        Some of the stats provided per variable are: avg, max, min, sum, range,
        stdev, q1, q3, median and interquartile_range

        Args:
            autoformat (boolean): set automatic format for values. Default is True.

        Example:

            .. code::

                # avg                    average value
                # max                    max value
                # min                    min value
                # sum                    sum of all values
                # range
                # stdev                  standard deviation
                # q1                     first quantile
                # q3                     third quantile
                # median                 median value
                # interquartile_range

        """
        FLOAT_FORMAT = 'display.float_format'

        if autoformat:
            pd.set_option(FLOAT_FORMAT, lambda x: '%.3f' % x)

        data = self.data['summary_json']
        return variable_describe(data)

    def head(self):
        """Returns a sample of the 10 first values of the variable data.

        For the cases of datasets with a content fewer than 10 rows
        (i.e. zip codes of small countries), this method won't return anything

        """
        data = self.data['summary_json']
        return head(self.__class__, data)

    def tail(self):
        """Returns a sample of the 10 last values of the variable data.

        For the cases of datasets with a content fewer than 10 rows
        (i.e. zip codes of small countries), this method won't return anything

        """
        data = self.data['summary_json']
        return tail(self.__class__, data)

    def counts(self):
        """Returns a summary of different counts over the actual variable values.

        Example:

            .. code::

                # all               total number of values
                # null              total number of null values
                # zero              number of zero-valued entries
                # extreme           number of values 3stdev outside the interquartile range
                # distinct          number of distinct (unique) entries
                # outliers          number of outliers (outside 1.5stdev the interquartile range
                # zero_percent      percent of values that are zero
                # distinct_percent  percent of values that are distinct

        """
        data = self.data['summary_json']
        return counts(data)

    def quantiles(self):
        """Returns the quantiles of the variable data."""
        data = self.data['summary_json']
        return quantiles(data)

    def top_values(self):
        """Returns information about the top values of the variable data."""
        data = self.data['summary_json']
        return top_values(data)

    def histogram(self):
        """Plots an histogram with the variable data."""
        data = self.data['summary_json']
        return histogram(data)

    def __repr__(self):
        descr = self.description

        if descr and len(descr) > _DESCRIPTION_LENGTH_LIMIT:
            descr = descr[0:_DESCRIPTION_LENGTH_LIMIT] + '...'

        return "<{classname}.get('{entity_id}')> #'{descr}'" \
               .format(classname=self.__class__.__name__, entity_id=self._get_print_id(), descr=descr)
