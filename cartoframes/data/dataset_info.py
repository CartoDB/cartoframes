import time
from warnings import warn

from carto.datasets import DatasetManager
from carto.exceptions import CartoException

from .utils import setting_value_exception
from .columns import normalize_name


class DatasetInfo(object):
    PRIVATE = 'PRIVATE'
    PUBLIC = 'PUBLIC'
    LINK = 'LINK'

    def __init__(self, context, table_name):
        self._metadata = self._get_metadata(context, table_name)
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

    def _get_metadata(self, context, table_name, retries=6, retry_wait_time=1):
        ds_manager = DatasetManager(context.auth_client)
        try:
            return ds_manager.get(table_name)
        except Exception as e:
            if type(e).__name__ == 'NotFoundException' and retries > 0:
                # if retry_wait_time > 7: # it should be after more than 15 seconds
                # warn('We are still procesing the CARTO table. Sorry for the delay.')
                time.sleep(retry_wait_time)
                self._get_metadata(context=context, table_name=table_name,
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
        if privacy not in [self.PRIVATE, self.PUBLIC, self.LINK]:
            raise ValueError('Wrong privacy. The privacy: {p} is not valid. You can use: {o1}, {o2}, {o3}'.format(
                p=privacy, o1=self.PRIVATE, o2=self.PUBLIC, o3=self.LINK))

        if privacy != self._privacy:
            return True

        return False

    def _validate_name(self, name):
        if name != self._table_name:
            return True

        return False
