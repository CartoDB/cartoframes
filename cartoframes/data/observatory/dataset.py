from __future__ import absolute_import

import pandas as pd
import geopandas as gpd
from shapely import wkt
from cartoframes.data import Dataset as CFDataset

from .entity import CatalogEntity
from .repository.dataset_repo import get_dataset_repo
from .repository.geography_repo import get_geography_repo
from .repository.variable_repo import get_variable_repo
from .repository.variable_group_repo import get_variable_group_repo
from .repository.constants import DATASET_FILTER
from .summary import dataset_describe, head, tail, counts, fields_by_type, geom_coverage
from . import subscription_info
from . import subscriptions
from . import utils

DATASET_TYPE = 'dataset'


class CatalogDataset(CatalogEntity):
    entity_repo = get_dataset_repo()

    @property
    def variables(self):
        return get_variable_repo().get_all({DATASET_FILTER: self.id})

    @property
    def variables_groups(self):
        return get_variable_group_repo().get_all({DATASET_FILTER: self.id})

    @property
    def name(self):
        return self.data['name']

    @property
    def description(self):
        return self.data['description']

    @property
    def provider(self):
        return self.data['provider_id']

    @property
    def category(self):
        return self.data['category_id']

    @property
    def data_source(self):
        return self.data['data_source_id']

    @property
    def country(self):
        return self.data['country_id']

    @property
    def language(self):
        return self.data['lang']

    @property
    def geography(self):
        return self.data['geography_id']

    @property
    def temporal_aggregation(self):
        return self.data['temporal_aggregation']

    @property
    def time_coverage(self):
        return self.data['time_coverage']

    @property
    def update_frequency(self):
        return self.data['update_frequency']

    @property
    def version(self):
        return self.data['version']

    @property
    def is_public_data(self):
        return self.data['is_public_data']

    @property
    def summary(self):
        return self.data['summary_json']

    def head(self):
        data = self.data['summary_json']
        return head(self.__class__, data)

    def tail(self):
        data = self.data['summary_json']
        return tail(self.__class__, data)

    def counts(self):
        data = self.data['summary_json']
        return counts(data)

    def fields_by_type(self):
        data = self.data['summary_json']
        return fields_by_type(data)

    def geom_coverage(self):
        return geom_coverage(self.geography)

    def describe(self):
        return dataset_describe(self.variables)

    @classmethod
    def get_all(cls, filters=None, credentials=None):
        return cls.entity_repo.get_all(filters, credentials)

    def download(self, credentials=None):
        """Download Dataset data.

        Args:
            credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
                credentials of CARTO user account. If not provided,
                a default credentials (if set with :py:meth:`set_default_credentials
                <cartoframes.auth.set_default_credentials>`) will be used.
        """

        return self._download(credentials)

    @classmethod
    def get_datasets_spatial_filtered(cls, filter_dataset):
        user_gdf = cls._get_user_geodataframe(filter_dataset)

        # TODO: check if the dataframe has a geometry column if not exception
        # Saving memory
        user_gdf = user_gdf[[user_gdf.geometry.name]]
        catalog_geographies_gdf = get_geography_repo().get_geographies_gdf()
        matched_geographies_ids = cls._join_geographies_geodataframes(catalog_geographies_gdf, user_gdf)

        # Get Dataset objects
        return get_dataset_repo().get_all({'geography_id': matched_geographies_ids})

    @staticmethod
    def _get_user_geodataframe(filter_dataset):
        if isinstance(filter_dataset, gpd.GeoDataFrame):
            # Geopandas dataframe
            return filter_dataset

        if isinstance(filter_dataset, CFDataset):
            # CARTOFrames Dataset
            user_df = filter_dataset.download(decode_geom=True)
            return gpd.GeoDataFrame(user_df, geometry='geometry')

        if isinstance(filter_dataset, str):
            # String WKT
            df = pd.DataFrame([{'geometry': filter_dataset}])
            df['geometry'] = df['geometry'].apply(wkt.loads)
            return gpd.GeoDataFrame(df)

    @staticmethod
    def _join_geographies_geodataframes(geographies_gdf1, geographies_gdf2):
        join_gdf = gpd.sjoin(geographies_gdf1, geographies_gdf2, how='inner', op='intersects')
        return join_gdf['id'].unique()

    def subscribe(self, credentials=None):
        """Subscribe to a Dataset.

        Args:
            credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
                credentials of CARTO user account. If not provided,
                a default credentials (if set with :py:meth:`set_default_credentials
                <cartoframes.auth.set_default_credentials>`) will be used.
        """

        _credentials = self._get_credentials(credentials)
        _subscribed_ids = subscriptions.get_subscription_ids(_credentials)

        if self.id in _subscribed_ids:
            utils.display_existing_subscription_message(self.id, DATASET_TYPE)
        else:
            utils.display_subscription_form(self.id, DATASET_TYPE, _credentials)

    def subscription_info(self, credentials=None):
        """Get the subscription information of a Dataset.

        Args:
            credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
                credentials of CARTO user account. If not provided,
                a default credentials (if set with :py:meth:`set_default_credentials
                <cartoframes.auth.set_default_credentials>`) will be used.
        """

        _credentials = self._get_credentials(credentials)

        return subscription_info.SubscriptionInfo(
            subscription_info.fetch_subscription_info(self.id, DATASET_TYPE, _credentials))
