
from carto.do_subscription_info import DOSubscriptionInfoManager


class SubscriptionInfo(object):

    def __init__(self, raw_data):
        self._raw_data = raw_data

    def __repr__(self):
        props = ['id', 'estimated_delivery_days', 'subscription_list_price',
                 'tos', 'tos_link', 'licenses', 'licenses_link', 'rights']
        return 'Properties: {}'.format(', '.join(props))

    @property
    def id(self):
        return self._raw_data.get('id')

    @property
    def estimated_delivery_days(self):
        return self._raw_data.get('estimated_delivery_days')

    @property
    def subscription_list_price(self):
        return self._raw_data.get('subscription_list_price')

    @property
    def tos(self):
        return self._raw_data.get('tos')

    @property
    def tos_link(self):
        return self._raw_data.get('tos_link')

    @property
    def licenses(self):
        return self._raw_data.get('licenses')

    @property
    def licenses_link(self):
        return self._raw_data.get('licenses_link')

    @property
    def rights(self):
        return self._raw_data.get('rights')


def fetch_subscription_info(id, type, credentials):
    api_key_auth_client = credentials.get_api_key_auth_client()
    do_manager = DOSubscriptionInfoManager(api_key_auth_client)
    return _resource_to_dict(do_manager.get(id, type))


def _resource_to_dict(resource):
    return {field: getattr(resource, field) for field in resource.fields}
