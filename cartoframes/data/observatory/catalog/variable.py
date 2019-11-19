from __future__ import absolute_import

from .entity import CatalogEntity
from .repository.dataset_repo import get_dataset_repo
from .repository.variable_repo import get_variable_repo
from .repository.constants import VARIABLE_FILTER
from .summary import variable_describe, head, tail, counts, quantiles, top_values, histogram


_DESCRIPTION_LENGTH_LIMIT = 30


class Variable(CatalogEntity):
    """This class represents a :py:class:`Variable <cartoframes.data.observatory.Variable>`
    of datasets in the :py:class:`Catalog <cartoframes.data.observatory.Catalog>`.

    Variables contain column names, description, data type, aggregation method and some other metadata that is
    useful to understand the underlying data inside a :obj:`CatalogDataset`

    Examples:
        List the variables of a :py:class:`CatalogDataset <cartoframes.data.observatory.CatalogDataset>`
        in combination with nested filters (categories, countries, etc.)

        .. code::

            from cartoframes.data.observatory import Catalog

            catalog = new Catalog()
            dataset = catalog.country('usa').category('demographics').datasets.get('mbi_retail_turn_705247a')
            dataset.variables
    """

    _entity_repo = get_variable_repo()

    @property
    def datasets(self):
        """Get the list of datasets related to this variable.

        Returns:
            :py:class:`CatalogList <cartoframes.data.observatory.entity.CatalogList>` List of Dataset instances.

        :raises DiscoveryException: When no datasets found.
        :raises CartoException: If there's a problem when connecting to the catalog.
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
        """Column name of the actual table related to the variable in the :obj:`CatalogDataset`."""
        return self.data['column_name']

    @property
    def db_type(self):
        """Type in the database.

        Examples: INTEGER, STRING, FLOAT, GEOGRAPHY, JSON, BOOL, etc.
        """
        return self.data['db_type']

    @property
    def dataset(self):
        """ID of the :obj:`CatalogDataset` to which this variable belongs."""

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
    def starred(self):
        """Boolean indicating whether this variable is a starred one or not. Internal usage only"""

        return self.data['starred']

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

    def describe(self):
        """Shows a summary of the actual stats of the variable (column) of the dataset.
        Some of the stats provided per variable are: avg, max, min, sum, range,
        stdev, q1, q3, median and interquartile_range

        Example:

            .. code::

                # avg                    6.781847e+01
                # max                    4.138516e+04
                # min                    0.000000e+00
                # sum                    3.272149e+08
                # range                  4.138516e+04
                # stdev                  1.654868e+02
                # q1                     8.090000e+00
                # q3                     3.882000e+01
                # median                 2.042000e+01
                # interquartile_range    3.073000e+01
        """
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

                # all                 4.854239e+06
                # null                2.937500e+04
                # zero                4.820100e+05
                # extreme             6.329720e+05
                # distinct            8.473600e+04
                # outliers            1.009540e+06
                # zero_percent        9.929672e+00
                # distinct_percent    1.745608e+00
        """
        data = self.data['summary_json']
        return counts(data)

    def quantiles(self):
        """Returns information about the quantiles of the variable data.

        Example:

            .. code::

                # q1                      8.09
                # q3                     38.82
                # median                 20.42
                # interquartile_range    30.73
        """
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

        return "<{classname}('{entity_id}','{descr}')>"\
               .format(classname=self.__class__.__name__, entity_id=self._get_print_id(), descr=descr)
