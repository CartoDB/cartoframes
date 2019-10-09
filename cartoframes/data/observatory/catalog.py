from __future__ import absolute_import

from .category import Category
from .country import Country
from .dataset import Dataset
from .geography import Geography
from .subscriptions import Subscriptions

from ...auth import Credentials, get_default_credentials


class Catalog(object):
    """Data Observatory Catalog"""

    @property
    def countries(self):
        """Get all the countries in the Catalog

        Returns:
            :py:class:`Categories <cartoframes.data.observatory.Countries>`

        """

        return Country.get_all()

    @property
    def categories(self):
        """Get all the categories in the Catalog

        Returns:
            :py:class:`Categories <cartoframes.data.observatory.Categories>`

        """

        return Category.get_all()

    @property
    def datasets(self):
        """Get all the datasets in the Catalog

        Returns:
            :py:class:`Datasets <cartoframes.data.observatory.Datasets>`

        """

        return Dataset.get_all()

    @classmethod
    def subscriptions(self, credentials=None):
        """Get all the subscriptions in the Catalog

        Args:
            credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
                A :py:class:`Credentials <cartoframes.auth.Credentials>`
                instance can be used in place of a `username`|`base_url` / `api_key` combination.

        Returns:
            :py:class:`Datasets <cartoframes.data.observatory.Datasets>`

        """

        _credentials = credentials or get_default_credentials()

        if not isinstance(credentials, Credentials):
            raise ValueError('`credentials` must be a Credentials class instance')

        return Subscriptions(
            Dataset.get_all(_credentials),
            Geography.get_all(_credentials)
        )
