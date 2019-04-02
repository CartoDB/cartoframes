from .datasets import Dataset


class CARTOframes(object):
    def __init__(self, carto_context):
        self.cc = carto_context

    def write(self, df, table_name, with_lonlat=None, if_exists='fail'):
        dataset = Dataset(self.cc, table_name, df=df)
        return dataset.upload(with_lonlat=with_lonlat, if_exists=if_exists)
