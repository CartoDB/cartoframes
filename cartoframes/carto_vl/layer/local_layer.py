from __future__ import absolute_import
from .query_layer import QueryLayer
import numpy as np
try:
    import geopandas
    HAS_GEOPANDAS = True
except ImportError:
    HAS_GEOPANDAS = False


class LocalLayer(QueryLayer):  # pylint: disable=too-few-public-methods
    """Create a layer from a GeoDataFrame

    TODO: add support JSON/dict or string

    See :obj:`QueryLayer` for the full styling documentation.

    Example:
        In this example, we grab data from the cartoframes example account
        using `read_mcdonals_nyc` to get McDonald's locations within New York
        City. Using the `decode_geom=True` argument, we decode the geometries
        into a form that works with GeoPandas. Finally, we pass the
        GeoDataFrame into :py:class:`LocalLayer
        <cartoframes.carto_vl.carto.LocalLayer>` to visualize.

        .. code::

            import geopandas
            from cartoframes.examples import read_mcdonalds_nyc, example_context
            from cartoframes import carto_vl as vl

            geodataframe = geopandas.GeoDataFrame(read_mcdonalds_nyc(decode_geom=True))

            vl.Map(
                [vl.LocalLayer(geodataframe)],
                context=example_context
            )


        It's also posible to load a local `.geojson` file by using `geopandas.read_file`
        method.

        .. code::

            import json
            import geopandas
            from cartoframes.examples import example_context
            from cartoframes import carto_vl as vl

            geojson = geopandas.read_file('points.geojson')

            vl.Map(
                [vl.LocalLayer(geojson)],
                context=example_context
            )
    """
    def __init__(self,
                 dataframe,
                 style=None,
                 variables=None,
                 interactivity=None,
                 legend=None):

        if HAS_GEOPANDAS and isinstance(dataframe, geopandas.GeoDataFrame):
            # filter out null geometries
            _df_nonnull = dataframe[~dataframe.geometry.isna()]
            # convert time cols to epoch
            timecols = _df_nonnull.select_dtypes(
                    include=['datetimetz', 'datetime', 'timedelta']).columns
            for timecol in timecols:
                _df_nonnull[timecol] = _df_nonnull[timecol].astype(np.int64)
            self._geojson_str = _df_nonnull.to_json()
            self.bounds = _df_nonnull.total_bounds.tolist()
        else:
            raise ValueError('LocalLayer only works with GeoDataFrames from '
                             'the geopandas package')

        super(LocalLayer, self).__init__(
            query=None,
            style=style,
            variables=variables,
            legend=legend,
            interactivity=interactivity
        )
