from abc import ABC, abstractmethod

from .repo_client import RepoClient
from ..entity import CatalogList, is_slug_value
from .....exceptions import CatalogError
from ..subscriptions import get_subscription_ids


def check_catalog_connection(method):
    def fn(*args, **kw):
        try:
            return method(*args, **kw)
        except Exception as e:
            raise CatalogError(
                'We are sorry, There\'s a problem when connecting to the catalog: {}'.format(e))
    return fn


class EntityRepository(ABC):

    def __init__(self, id_field, filters=[], slug_field=None):
        self.client = RepoClient()

        self.id_field = id_field
        self.allowed_filters = filters + [id_field]
        self.slug_field = slug_field

        if slug_field:
            self.allowed_filters.append(slug_field)

    def get_all(self, filters=None):
        return self._get_filtered_entities(filters)

    def get_by_id(self, entity_id):
        result = self._get_filtered_entity(entity_id)

        if len(result) == 0:
            raise CatalogError('The id does not correspond with any existing entity in the catalog. '
                               'You can check the full list of available values with get_all() method.')

        data = self._map_row(result[0])
        return self._to_catalog_entity(data)

    def get_by_id_list(self, id_list):
        return self._get_filtered_entities(self._get_id_list_filters(id_list))

    @check_catalog_connection
    def _get_filtered_entity(self, entity_id):
        return self._get_rows(self._get_id_filter(entity_id))

    @check_catalog_connection
    def _get_filtered_entities(self, filters):
        cleaned_filters = self._get_filters(filters)
        rows = self._get_rows(cleaned_filters)

        if len(rows) == 0:
            return None

        normalized_data = [self._get_entity_class()(self._map_row(row)) for row in rows]
        return CatalogList(normalized_data)

    def _get_filters(self, filters):
        if filters is not None:
            cleaned_filters = {field: value for field, value in filters.items() if field in self.allowed_filters}
            return cleaned_filters

    def _get_id_filter(self, id_):
        if self.slug_field is not None and is_slug_value(id_):
            return {self.slug_field: [id_]}

        return {self.id_field: [id_]}

    def _get_id_list_filters(self, id_list):
        if self.slug_field is None:
            return {self.id_field: id_list}

        ids = []
        slugs = []
        filters = {}

        for id_ in id_list:
            if is_slug_value(id_):
                slugs.append(id_)
            else:
                ids.append(id_)

        if len(ids) > 0:
            filters[self.id_field] = ids

        if len(slugs) > 0:
            filters[self.slug_field] = slugs

        return filters

    def _add_subscription_ids(self, filters, credentials, entity_type):
        ids = get_subscription_ids(credentials, entity_type)

        if not isinstance(ids, list) or len(ids) == 0:
            return None

        filters = filters or {}
        filters['id'] = ids
        return filters

    @classmethod
    def _to_catalog_entity(cls, result):
        return cls._get_entity_class()(result)

    @classmethod
    def _normalize_field(cls, row, field):
        return row.get(field, None)

    @classmethod
    @abstractmethod
    def _get_entity_class(cls):
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def _map_row(cls, row):
        raise NotImplementedError

    @abstractmethod
    def _get_rows(self, filters=None):
        raise NotImplementedError
