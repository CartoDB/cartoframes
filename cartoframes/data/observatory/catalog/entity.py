import pandas as pd
from warnings import warn

from google.api_core.exceptions import NotFound

from carto.exceptions import CartoException

from ...clients.bigquery_client import BigQueryClient
from ....auth import Credentials, defaults

try:
    from abc import ABC
except ImportError:
    from abc import ABCMeta
    ABC = ABCMeta('ABC', (object,), {'__slots__': ()})

_WORKING_PROJECT = 'carto-do-customers'
_PLATFORM_BQ = 'bq'


class CatalogEntity(ABC):
    """
    This is an internal class the rest of the classes related to the catalog discovery extend.

    It contains:
      - Properties: `id`, `slug` (a shorter ID).
      - Static methods: `get`, `get_all`, `get_list` to retrieve elements or lists of objects in the catalog such as
        datasets, categories, variables, etc.
      - Instance methods to convert to pandas Series, Python dict, compare instances, etc.

    As a rule of thumb you don't use directly this class, it is documented for inheritance purposes.
    """

    id_field = 'id'
    _entity_repo = None
    export_excluded_fields = ['summary_json', 'available_in', 'geom_coverage']

    def __init__(self, data):
        self.data = data

    @property
    def id(self):
        """The ID of the entity."""
        return self.data[self.id_field]

    @property
    def slug(self):
        """The slug (short ID) of the entity."""
        try:
            return self.data['slug']
        except KeyError:
            return None

    @classmethod
    def get(cls, id_):
        """Get an instance of an entity by ID or slug.

        Args:
            id_ (str):
                ID or slug of a catalog entity.

        :raises DiscoveryException: When no entities found.
        :raises CartoException: If there's a problem when connecting to the catalog.
        """
        return cls._entity_repo.get_by_id(id_)

    @classmethod
    def get_all(cls, filters=None):
        """List all instances of an entity.

        Args:
            filters (dict, optional):
                Dict containing pairs of entity properties and its value to be used as filters to query the available
                entities. If none is provided, no filters will be applied to the query.
        """
        return cls._entity_repo.get_all(filters)

    @classmethod
    def get_list(cls, id_list):
        """Get a list of instance of an entity by a list of IDs or slugs.

        Args:
            id_list (list):
                List of sD or slugs of a entities in the catalog to retrieve instances.

        :raises DiscoveryException: When no entities found.
        :raises CartoException: If there's a problem when connecting to the catalog.
        """
        return cls._entity_repo.get_by_id_list(id_list)

    def to_series(self):
        """Converts the entity instance to a pandas Series."""
        return pd.Series(self.data)

    def to_dict(self):
        """Converts the entity instance to a Python dict."""
        return {key: value for key, value in self.data.items() if key not in self.export_excluded_fields}

    def __eq__(self, other):
        return self.data == other.data

    def __ne__(self, other):
        return not self == other

    def __str__(self):
        return '{classname}({data})'.format(classname=self.__class__.__name__, data=self.data.__str__())

    def __repr__(self):
        id = self._get_print_id()
        return "<{classname}.get('{entity_id}')>".format(classname=self.__class__.__name__, entity_id=id)

    def _get_print_id(self):
        if 'slug' in self.data.keys():
            return self.data['slug']

        return self.id

    def _download(self, credentials=None):
        if not self._is_available_in('bq'):
            raise CartoException('{} is not ready for Download. Please, contact us for more information.'.format(self))

        credentials = self._get_credentials(credentials)
        user_dataset = credentials.get_do_user_dataset()
        bq_client = _get_bigquery_client(_WORKING_PROJECT, credentials)

        project, dataset, table = self.id.split('.')
        view = 'view_{}_{}'.format(dataset.replace('-', '_'), table)

        try:
            file_path = bq_client.download_to_file(_WORKING_PROJECT, user_dataset, view)
        except NotFound:
            raise CartoException('You have not purchased the dataset `{}` yet'.format(self.id))

        warn('Data saved: {}.'.format(file_path))
        warn("To read it you can do: `pandas.read_csv('{}')`.".format(file_path))

        return file_path

    def _is_available_in(self, platform=_PLATFORM_BQ):
        return self.data['available_in'] and platform in self.data['available_in']

    def _get_credentials(self, credentials=None):
        _credentials = credentials or defaults.get_default_credentials()

        if not isinstance(_credentials, Credentials):
            raise ValueError('`credentials` must be a Credentials class instance')

        return _credentials


def _get_bigquery_client(project, credentials):
    return BigQueryClient(project, credentials)


def is_slug_value(id_value):
    return len(id_value.split('.')) == 1


class CatalogList(list):
    """
    This is an internal class that represents a list of entities in the catalog of the same type.

    It contains:
      - Instance methods to convert to get an instance of the entity by ID and to convert the list to a pandas
        DataFrame for further filtering and exploration.

    As a rule of thumb you don't use directly this class, it is documented for inheritance purposes.
    """

    def __init__(self, data):
        super(CatalogList, self).__init__(data)

    def get(self, item_id):
        """Gets an entity by ID or slug

        Examples:

            .. code::

                from cartoframes.data.observatory import Catalog

                catalog = Catalog()
                category = catalog.categories.get('demographics')

        """
        return next(iter(filter(lambda item: item.id == item_id or item.slug == item_id, self)), None)

    def to_dataframe(self):
        """Converts a list to a pandas DataFrame.

        Examples:

            .. code::

                from cartoframes.data.observatory import Catalog

                catalog = Catalog()
                catalog.categories.to_dataframe()
        """
        return pd.DataFrame([item.data for item in self])
