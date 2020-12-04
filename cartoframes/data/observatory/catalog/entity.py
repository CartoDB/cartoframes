import pandas as pd

from abc import ABC
from geopandas import GeoDataFrame

from carto.do_dataset import DODataset
from . import subscriptions
from ....utils.geom_utils import set_geometry
from ....utils.logger import log

_DATASET_READ_MSG = '''To load it as a DataFrame you can do:

    df = pandas.read_csv('{}')
'''

_GEOGRAPHY_READ_MSG = '''To load it as a GeoDataFrame you can do:

    from cartoframes.utils import decode_geometry

    df = pandas.read_csv('{}')
    gdf = GeoDataFrame(df, geometry=decode_geometry(df['geom']))
'''

GEOM_COL = 'geom'


class CatalogEntity(ABC):
    """This is an internal class the rest of the classes related to the catalog discovery extend.

    It contains:
      - Properties: `id`, `slug` (a shorter ID).
      - Static methods: `get`, `get_all`, `get_list` to retrieve elements or lists of objects in the catalog such as
        datasets, categories, variables, etc.
      - Instance methods to convert to pandas Series, Python dict, compare instances, etc.

    As a rule of thumb you don't directly use this class, it is documented for inheritance purposes.

    """
    id_field = 'id'
    _entity_repo = None
    export_excluded_fields = ['summary_json', 'geom_coverage']

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

        Raises:
            CatalogError: if there's a problem when connecting to the catalog or no entities are found.

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
                List of ID or slugs of entities in the catalog to retrieve instances.

        Raises:
            CatalogError: if there's a problem when connecting to the catalog or no entities are found.

        """
        return cls._entity_repo.get_by_id_list(id_list)

    def to_series(self):
        """Converts the entity instance to a pandas Series."""
        return pd.Series(self.data)

    def to_dict(self):
        """Converts the entity instance to a Python dict."""
        return {key: value for key, value in self.data.items() if key not in self.export_excluded_fields}

    def is_subscribed(self, credentials, entity_type):
        """Check if the entity is subscribed"""
        return self.is_public_data or self.id in subscriptions.get_subscription_ids(credentials, entity_type)

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

    def _download(self, credentials, file_path=None, limit=None, order_by=None, sql_query=None, add_geom=None):
        auth_client = credentials.get_api_key_auth_client()

        is_geography = None
        if sql_query is not None:
            is_geography = self.__class__.__name__ == 'Geography'

        rows = DODataset(auth_client=auth_client).name(self.id).download_stream(limit=limit,
                                                                                order_by=order_by,
                                                                                sql_query=sql_query,
                                                                                add_geom=add_geom,
                                                                                is_geography=is_geography)
        if file_path:
            with open(file_path, 'w') as csvfile:
                for row in rows:
                    csvfile.write(row.decode('utf-8'))

            log.info('Data saved: {}'.format(file_path))
            if self.__class__.__name__ == 'Dataset':
                log.info(_DATASET_READ_MSG.format(file_path))
            elif self.__class__.__name__ == 'Geography':
                log.info(_GEOGRAPHY_READ_MSG.format(file_path))
        else:
            dataframe = pd.read_csv(rows)
            gdf = GeoDataFrame(dataframe)

            if GEOM_COL in gdf:
                set_geometry(gdf, GEOM_COL, inplace=True)

            return gdf

    def _get_remote_full_table_name(self, user_project, user_dataset, public_project):
        project, dataset, table = self.id.split('.')

        if project != public_project:
            return '{project}.{dataset}.{table_name}'.format(
                project=user_project,
                dataset=user_dataset,
                table_name='view_{}_{}'.format(dataset, table)
            )
        else:
            return self.id


def is_slug_value(id_value):
    return len(id_value.split('.')) == 1


class CatalogList(list):
    """This is an internal class that represents a list of entities in the catalog of the same type.

    It contains:
      - Instance methods to convert to get an instance of the entity by ID and to convert the list to a pandas
        DataFrame for further filtering and exploration.

    As a rule of thumb you don't directly use this class, it is documented for inheritance purposes.

    """
    def __init__(self, data):
        super(CatalogList, self).__init__(data)

    def to_dataframe(self):
        """Converts a list to a pandas DataFrame.

        Examples:
            >>> catalog = Catalog()
            >>> catalog.categories.to_dataframe()

        """
        df = pd.DataFrame([item.data for item in self])

        if 'summary_json' in df:
            del df['summary_json']

        return df
