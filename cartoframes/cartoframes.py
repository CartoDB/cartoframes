from .datasets import Dataset
from .context import CartoContext


class CARTOframes(object):
    def __init__(self, base_url=None, api_key=None, creds=None, session=None,
                 verbose=0):
        self.cc = CartoContext(base_url=base_url, api_key=api_key, creds=creds, session=session, verbose=verbose)

    def write(self, df, table_name, with_lonlat=None, if_exists=Dataset.FAIL):
        dataset = Dataset(self.cc, table_name, df=df)
        return dataset.upload(with_lonlat=with_lonlat, if_exists=if_exists)
