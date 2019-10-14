from __future__ import absolute_import

from .entity import CatalogEntity
from .repository.dataset_repo import get_dataset_repo
from .repository.variable_repo import get_variable_repo
from .repository.constants import VARIABLE_FILTER


_DESCRIPTION_LENGTH_LIMIT = 20


class Variable(CatalogEntity):

    entity_repo = get_variable_repo()

    @property
    def datasets(self):
        return get_dataset_repo().get_all({VARIABLE_FILTER: self.id})

    @property
    def name(self):
        return self.data['name']

    @property
    def description(self):
        return self.data['description']

    @property
    def column_name(self):
        return self.data['column_name']

    @property
    def db_type(self):
        return self.data['db_type']

    @property
    def dataset(self):
        return self.data['dataset_id']

    @property
    def agg_method(self):
        return self.data['agg_method']

    @property
    def variable_group(self):
        return self.data['variable_group_id']

    @property
    def starred(self):
        return self.data['starred']

    @property
    def summary(self):
        return self.data['summary_jsonb']

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

    def __repr__(self):
        descr = self.description

        if len(descr) > _DESCRIPTION_LENGTH_LIMIT:
            descr = descr[0:_DESCRIPTION_LENGTH_LIMIT] + '...'

        return "<{classname}('{entity_id}','{descr}')>"\
               .format(classname=self.__class__.__name__, entity_id=self._get_print_id(), descr=descr)

