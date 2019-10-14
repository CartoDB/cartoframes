from __future__ import absolute_import


from .entity import CatalogEntity
from .repository.dataset_repo import get_dataset_repo
from .repository.variable_repo import get_variable_repo
from .repository.variable_group_repo import get_variable_group_repo
from .repository.geography_repo import get_geography_repo
from .repository.constants import DATASET_FILTER

import geopandas as gpd
import pandas as pd
from cartoframes.data import Dataset as CFDataset
from shapely import wkt
from .utils import display_subscription_form

class Dataset(CatalogEntity):
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
        return self.data['summary_jsonb']

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
    def datasets_by_geography(cls, filter_dataset):

        if isinstance(filter_dataset, gpd.GeoDataFrame):
            # Geopandas dataframe
            user_gdf = filter_dataset
            
        elif isinstance(filter_dataset, CFDataset):
            # CARTOFrames Dataset
            user_df = filter_dataset.download(decode_geom=True)
            user_gdf = gpd.GeoDataFrame(user_df, geometry='geometry')

        elif isinstance(filter_dataset, str):
            ## String WKT
            df = pd.DataFrame([{'geometry': filter_dataset}])
            df['geometry'] = df['geometry'].apply(wkt.loads)
            user_gdf = gpd.GeoDataFrame(df)

        ##TODO: check if the dataframe has a geometry column if not exception
        # Saving memory
        user_gdf = user_gdf[[user_gdf.geometry.name]]

        geography_repo = get_geography_repo()
        # Get catalog geographies as a geodataframe
        geographies_gdf = geography_repo.get_geographies_gdf()

        # Join both dataframes
        join_gdf = gpd.sjoin(geographies_gdf, user_gdf, how='inner', op='intersects')
        matched_boundaries = join_gdf['id'].unique()
        
        # Get Dataset objects
        return cls.entity_repo.get_datasets_for_geographies(matched_boundaries)
        
       
    def subscribe(self, credentials=None):
        """Subscribe to a Dataset.

        Args:
            credentials (:py:class:`Credentials <cartoframes.auth.Credentials>`, optional):
                credentials of CARTO user account. If not provided,
                a default credentials (if set with :py:meth:`set_default_credentials
                <cartoframes.auth.set_default_credentials>`) will be used.
        """

        _credentials = self._get_credentials(credentials)

        display_subscription_form(self.id, 'dataset', _credentials)
