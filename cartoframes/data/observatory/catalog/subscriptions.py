
from carto.do_subscriptions import DOSubscriptionManager, DOSubscriptionCreationManager


class Subscriptions(object):

    def __init__(self, datasets, geographies):
        self._subscriptions_datasets = datasets
        self._subscriptions_geographies = geographies

    def __repr__(self):
        return 'Datasets: {0}\nGeographies: {1}'.format(
            self._subscriptions_datasets,
            self._subscriptions_geographies
        )

    @property
    def datasets(self):
        return self._subscriptions_datasets

    @property
    def geographies(self):
        return self._subscriptions_geographies


def get_subscription_ids(credentials):
    subscriptions = fetch_subscriptions(credentials)
    subscriptions_ids = list(map(lambda pd: pd.id, subscriptions))
    return ','.join(["'" + id + "'" for id in subscriptions_ids])


def fetch_subscriptions(credentials):
    if credentials:
        api_key_auth_client = credentials.get_api_key_auth_client()
        do_manager = DOSubscriptionManager(api_key_auth_client)
        if do_manager is not None:
            return do_manager.all()
    return []


def trigger_subscription(id, type, credentials):
    api_key_auth_client = credentials.get_api_key_auth_client()
    do_manager = DOSubscriptionCreationManager(api_key_auth_client)
    return do_manager.create(id=id, type=type)
