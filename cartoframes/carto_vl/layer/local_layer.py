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
            from cartoframes.carto_vl import carto

            geodataframe = geopandas.GeoDataFrame(read_mcdonalds_nyc(decode_geom=True))

            carto.Map(
                [carto.LocalLayer(geodataframe)],
                context=example_context
            ).init()


        It's also posible to load a local `.geojson` file by using `geopandas.read_file`
        method.

        .. code::

            import json
            import geopandas
            from cartoframes.examples import example_context
            from cartoframes.carto_vl import carto

            geojson = geopandas.read_file('points.geojson')

            carto.Map(
                [carto.LocalLayer(geojson)],
                context=example_context
            ).init()
    """
    def __init__(self,
                 dataframe,
                 viz=None,
                 color_=None,
                 width_=None,
                 filter_=None,
                 stroke_color_=None,
                 stroke_width_=None,
                 transform_=None,
                 order_=None,
                 symbol_=None,
                 variables=None,
                 legend=None,
                 interactivity=None):
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
            viz=viz,
            color_=color_,
            width_=width_,
            filter_=filter_,
            stroke_color_=stroke_color_,
            stroke_width_=stroke_width_,
            transform_=transform_,
            order_=order_,
            symbol_=symbol_,
            variables=variables,
            legend=legend,
            interactivity=interactivity
        )
