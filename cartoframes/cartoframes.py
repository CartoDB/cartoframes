from .dataset import Dataset
from .context import CartoContext


class CartoFrames(object):
    def __init__(self, base_url=None, api_key=None, creds=None, session=None,
                 verbose=0):
        self.cc = CartoContext(base_url=base_url, api_key=api_key, creds=creds, session=session, verbose=verbose)

    def write(self, df, table_name, with_lonlat=None, if_exists=Dataset.FAIL):
        dataset = Dataset.from_dataframe(df, table_name=table_name, context=self.cc)
        return dataset.upload(with_lonlat=with_lonlat, if_exists=if_exists)
