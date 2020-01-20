import time

from carto.datasets import DatasetManager

from warnings import filterwarnings
filterwarnings('ignore', category=FutureWarning, module='carto')


class DatasetInfo:
    PRIVACY_PRIVATE = 'PRIVATE'
    """Dataset privacy for datasets that are private"""

    PRIVACY_PUBLIC = 'PUBLIC'
    """Dataset privacy for datasets that are public"""

    PRIVACY_LINK = 'LINK'
    """Dataset privacy for datasets that are accessible by link"""

    def __init__(self, auth_client, table_name):
        self._metadata = self._get_metadata(auth_client, table_name)
        self._privacy = self._metadata.privacy if self._metadata is not None else None

    @property
    def privacy(self):
        return self._privacy

    def update_privacy(self, privacy=None):
        if privacy and self._validate_privacy(privacy):
            self._privacy = privacy.upper()
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
                raise Exception('We could not get the table metadata. '
                                'Please, try again in a few seconds or contact support for help')

    def _save_metadata(self):
        self._metadata.privacy = self._privacy
        self._metadata.save()

    def _validate_privacy(self, privacy):
        privacy = privacy.upper()
        if privacy not in [self.PRIVACY_PRIVATE, self.PRIVACY_PUBLIC, self.PRIVACY_LINK]:
            raise ValueError('Wrong privacy. The privacy: {p} is not valid. You can use: {o1}, {o2}, {o3}'.format(
                p=privacy, o1=self.PRIVACY_PRIVATE, o2=self.PRIVACY_PUBLIC, o3=self.PRIVACY_LINK))

        if privacy != self._privacy:
            return True

        return False
