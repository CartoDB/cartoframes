from __future__ import absolute_import

import time
from warnings import warn

from carto.datasets import DatasetManager
from carto.exceptions import CartoException

from ..utils.columns import normalize_name

from warnings import filterwarnings
filterwarnings("ignore", category=FutureWarning, module="carto")

# TODO: refactor


class DatasetInfo(object):
    PRIVACY_PRIVATE = 'PRIVATE'
    """Dataset privacy for datasets that are private"""

    PRIVACY_PUBLIC = 'PUBLIC'
    """Dataset privacy for datasets that are public"""

    PRIVACY_LINK = 'LINK'
    """Dataset privacy for datasets that are accessible by link"""

    def __init__(self, auth_client, table_name):
        self._metadata = self._get_metadata(auth_client, table_name)
        self._privacy = self._metadata.privacy
        self._table_name = self._metadata.name

    @property
    def privacy(self):
        return self._privacy

    @privacy.setter
    def privacy(self, privacy):
        raise setting_value_exception('privacy', privacy)

    @property
    def table_name(self):
        return self._table_name

    @table_name.setter
    def table_name(self, table_name):
        raise setting_value_exception('table_name', table_name)

    def update(self, privacy=None, table_name=None):
        modified = False

        if privacy and self._validate_privacy(privacy):
            self._privacy = privacy.upper()
            modified = True

        if table_name:
            normalized_name = normalize_name(table_name)
            if self._validate_name(normalized_name):
                self._table_name = normalized_name
                modified = True

                if self._table_name != table_name:
                    warn('Dataset name will be named `{}`'.format(self._table_name))

        if modified:
            self._save_metadata()

    def _get_metadata(self, auth_client, table_name, retries=4, retry_wait_time=1):
        ds_manager = DatasetManager(auth_client)
        try:
            return ds_manager.get(table_name)
        except Exception as e:
            if type(e).__name__ == 'NotFoundException' and retries > 0:
                time.sleep(retry_wait_time)
                self._get_metadata(auth_client=auth_client, table_name=table_name,
                                   retries=retries-1, retry_wait_time=retry_wait_time*2)
            else:
                raise CartoException('We could not get the table metadata. '
                                     'Please, try again in a few seconds or contact support for help')

    def _save_metadata(self):
        self._metadata.privacy = self._privacy
        self._metadata.name = self._table_name
        self._metadata.save()

    def _validate_privacy(self, privacy):
        privacy = privacy.upper()
        if privacy not in [self.PRIVACY_PRIVATE, self.PRIVACY_PUBLIC, self.PRIVACY_LINK]:
            raise ValueError('Wrong privacy. The privacy: {p} is not valid. You can use: {o1}, {o2}, {o3}'.format(
                p=privacy, o1=self.PRIVACY_PRIVATE, o2=self.PRIVACY_PUBLIC, o3=self.PRIVACY_LINK))

        if privacy != self._privacy:
            return True

        return False

    def _validate_name(self, name):
        if name != self._table_name:
            return True

        return False


def setting_value_exception(prop, value):
    return CartoException(("Error setting {prop}. You must use the `update` method: "
                           "dataset_info.update({prop}='{value}')").format(prop=prop, value=value))
