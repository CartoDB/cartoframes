from __future__ import absolute_import

from carto.exceptions import CartoException, CartoRateLimitException

from ....utils.geom_utils import get_context_with_public_creds
from ..dataset_info import DatasetInfo


class BaseDataset():

    @property
    def dataset_info(self):
        if self._dataset_info is None:
            self._dataset_info = self._get_dataset_info()

        return self._dataset_info

    def update_dataset_info(self, privacy=None, table_name=None):
        self._dataset_info = self.dataset_info
        self._dataset_info.update(privacy=privacy, table_name=table_name)

        # update table_name if metadata table_name has been changed
        if table_name and self.table_name != self._dataset_info.table_name:
            self.table_name = self._dataset_info.table_name

    def is_public(self):
        """Checks to see if table or table used by query has public privacy"""
        public_context = get_context_with_public_creds(self._credentials)
        try:
            public_context.execute_query('EXPLAIN {}'.format(self.get_query()), do_post=False)
            return True
        except CartoRateLimitException as err:
            raise err
        except CartoException:
            return False

    def get_table_names(self):
        return [self._table_name]

    def _get_dataset_info(self, table_name=None):
        return DatasetInfo(self._context, table_name or self._table_name)
