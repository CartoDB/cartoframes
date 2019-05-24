from carto.datasets import DatasetManager
from carto.exceptions import CartoException


class DatasetInfo():
    PRIVATE = 'PRIVATE'
    PUBLIC = 'PUBLIC'
    LINK = 'LINK'

    def __init__(self, carto_context, table_name):
        self._get_metadata(carto_context, table_name)

        if self._metadata is not None:
            self.privacy = self._metadata.privacy
            self.name = self._metadata.name
        else:
            raise CartoException('Something goes wrong accessing the table metadata.')

    def update(self, privacy=None, name=None):
        modified = False
        if privacy and self._validate_privacy(privacy):
            self.privacy = privacy.upper()
            modified = True
        if name and self._validate_name(name):
            self.name = name
            modified = True

        if modified:
            self._save_metadata()

    def _get_metadata(self, carto_context, table_name, retries=6, retry_wait_time=1):
        ds_manager = DatasetManager(carto_context.auth_client)
        try:
            self._metadata = ds_manager.get(table_name)
        except Exception as e:
            if type(e).__name__ == 'NotFoundException' and retries > 0:
                # if retry_wait_time > 7: # it should be after more than 15 seconds
                    # warn('We are still procesing the CARTO table. Sorry for the delay.')
                time.sleep(retry_wait_time)
                self._get_metadata(carto_context= carto_context, table_name=table_name,
                                   retries=retries-1, retry_wait_time=retry_wait_time*2)
            else:
                return None

    def _save_metadata(self):
        self._metadata.privacy = self.privacy
        self._metadata.name = self.name
        self._metadata.save()

    def _validate_privacy(self, privacy):
        if privacy.upper() not in [self.PRIVATE, self.PUBLIC, self.LINK]:
            raise ValueError('Wrong privacy. The privacy: {p} is not valid. You can use: {o1}, {o2}, {o3}'.format(
                p=privacy, o1=self.PRIVATE, o2=self.PUBLIC, o3=self.LINK))

        if privacy != self.privacy:
            return True

        return False

    def _validate_name(self, name):
        if name != self.name:
            return True

        return False
