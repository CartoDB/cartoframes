
from carto.do_subscription_info import DOSubscriptionInfoManager


class SubscriptionInfo:
    """This class represents a :py:class:`SubscriptionInfo <cartoframes.data.observatory.SubscriptionInfo>`
    of datasets and geographies in the :py:class:`Catalog <cartoframes.data.observatory.Catalog>`

    It contains private metadata (you need a CARTO account to query them) that is useful when you want a subscription
    license for a specific dataset or geography.

    """
    def __init__(self, raw_data):
        self._raw_data = raw_data

    def __repr__(self):
        props = ['id', 'estimated_delivery_days', 'subscription_list_price',
                 'tos', 'tos_link', 'licenses', 'licenses_link', 'rights']
        return 'Properties: {}'.format(', '.join(props))

    @property
    def id(self):
        """The ID of the dataset or geography."""
        return self._raw_data.get('id')

    @property
    def estimated_delivery_days(self):
        """Estimated days in which, once you :py:attr:`Dataset.subscribe` or :py:attr:`Geography.subscribe`,
        you'll get a license.

        Your licensed datasets and geographies will be returned by the
        :py:meth:`catalog.subscriptions <cartoframes.data.observatory.Catalog.subscriptions>` method.

        For the datasets and geographies listed in the
        :py:meth:`catalog.subscriptions <cartoframes.data.observatory.Catalog.subscriptions>` method you can:
        - :py:attr:`Dataset.download` or :py:attr:`Geography.download`
        - Use their `Dataset.variables` in the :obj:`Enrichment` functions
        """
        return self._raw_data.get('estimated_delivery_days')

    @property
    def subscription_list_price(self):
        """Price in $ for a one year subscription for this dataset."""
        return self._raw_data.get('subscription_list_price')

    @property
    def tos(self):
        """Legal Terms Of Service."""
        return self._raw_data.get('tos')

    @property
    def tos_link(self):
        """Link to additional information for the legal Terms Of Service."""
        return self._raw_data.get('tos_link')

    @property
    def licenses(self):
        """Description of the licenses."""
        return self._raw_data.get('licenses')

    @property
    def licenses_link(self):
        """Link to additional information about the available licenses."""
        return self._raw_data.get('licenses_link')

    @property
    def rights(self):
        """Rights over the dataset or geography when you buy a license by means of a subscription."""
        return self._raw_data.get('rights')


def fetch_subscription_info(id, type, credentials):
    api_key_auth_client = credentials.get_api_key_auth_client()
    do_manager = DOSubscriptionInfoManager(api_key_auth_client)
    return _resource_to_dict(do_manager.get(id, type))


def _resource_to_dict(resource):
    return {field: getattr(resource, field) for field in resource.fields}
