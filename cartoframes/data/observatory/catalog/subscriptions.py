
from json.decoder import JSONDecodeError
from carto.do_subscriptions import DOSubscriptionManager, DOSubscriptionCreationManager


class Subscriptions:
    """This class is used to list the datasets and geographies you have acquired a subscription (or valid license) for.

    This class won't show any dataset or geography tagged in the catalog as `is_public_data` since those data do not
    require a subscription.

    """
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
        """List of :obj:`Dataset` you have a subscription for.

        Raises:
            CatalogError: if there's a problem when connecting to the catalog.

        """
        return self._subscriptions_datasets

    @property
    def geographies(self):
        """List of :obj:`Geography` you have a subscription for.

        Raises:
            CatalogError: if there's a problem when connecting to the catalog.

        """
        return self._subscriptions_geographies


def get_subscription_ids(credentials, stype=None):
    subs = fetch_subscriptions(credentials)
    return [s.id for s in subs if stype is None or stype == s.type]


def fetch_subscriptions(credentials):
    if credentials:
        api_key_auth_client = credentials.get_api_key_auth_client()
        do_manager = DOSubscriptionManager(api_key_auth_client)
        if do_manager is not None:
            try:
                return do_manager.all()
            except JSONDecodeError:
                return []
    return []


def trigger_subscription(id, type, credentials):
    api_key_auth_client = credentials.get_api_key_auth_client()
    do_manager = DOSubscriptionCreationManager(api_key_auth_client)
    return do_manager.create(id=id, type=type)
