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


class CatalogEntity(ABC):

    id_field = 'id'
    entity_repo = None
    export_excluded_fields = ['summary_json']

    def __init__(self, data):
        self.data = data

    @property
    def id(self):
        return self.data[self.id_field]

    @property
    def slug(self):
        try:
            return self.data['slug']
        except KeyError:
            return None

    @classmethod
    def get(cls, id_):
        return cls.entity_repo.get_by_id(id_)

    @classmethod
    def get_all(cls, filters=None):
        return cls.entity_repo.get_all(filters)

    @classmethod
    def get_list(cls, id_list):
        return cls.entity_repo.get_by_id_list(id_list)

    def to_series(self):
        return pd.Series(self.data)

    def to_dict(self):
        return {key: value for key, value in self.data.items() if key not in self.export_excluded_fields}

    def __eq__(self, other):
        return self.data == other.data

    def __ne__(self, other):
        return not self == other

    def __str__(self):
        return '{classname}({data})'.format(classname=self.__class__.__name__, data=self.data.__str__())

    def __repr__(self):
        return "<{classname}('{entity_id}')>".format(classname=self.__class__.__name__, entity_id=self._get_print_id())

    def _get_print_id(self):
        if 'slug' in self.data.keys():
            return self.data['slug']

        return self.id

    def _download(self, credentials=None):
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

    def __init__(self, data):
        super(CatalogList, self).__init__(data)

    def get(self, item_id):
        return next(iter(filter(lambda item: item.id == item_id or item.slug == item_id, self)), None)

    def to_dataframe(self):
        return pd.DataFrame([item.data for item in self])
