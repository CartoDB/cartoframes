
class SubscriptionInfo(object):

    def __init__(self, raw_data):
        self._raw_data = raw_data

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
