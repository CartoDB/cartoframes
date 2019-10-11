
class Subscriptions(object):

    def __init__(self, datasets, geographies):
        self._subscriptions_datasets = datasets
        self._subscriptions_geographies = geographies

    @property
    def datasets(self):
        return self._subscriptions_datasets

    @property
    def geographies(self):
        return self._subscriptions_geographies
