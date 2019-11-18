from geopandas import GeoDataFrame

from ..utils.geom_utils import generate_index, generate_geometry


class CartoDataFrame(GeoDataFrame):

    def __init__(self, *args, **kwargs):
        index_column = kwargs.pop('index_column', None)
        geom_column = kwargs.pop('geom_column', None)
        lnglat_columns = kwargs.pop('lnglat_columns', None)
        drop_index = kwargs.pop('drop_index', True)
        drop_geom = kwargs.pop('drop_geom', True)
        drop_lnglat = kwargs.pop('drop_lnglat', True)

        super(CartoDataFrame, self).__init__(*args, **kwargs)

        generate_index(self, index_column, drop_index)
        generate_geometry(self, geom_column, lnglat_columns, drop_geom, drop_lnglat)

    @staticmethod
    def from_carto(*args, **kwargs):
        from ..io.carto import read_carto
        return read_carto(*args, **kwargs)

    @classmethod
    def from_file(cls, filename, **kwargs):
        gdf = GeoDataFrame.from_file(filename, **kwargs)
        return cls(gdf)

    @classmethod
    def from_features(cls, features, **kwargs):
        gdf = GeoDataFrame.from_features(features, **kwargs)
        return cls(gdf)

    def to_carto(self, *args, **kwargs):
        from ..io.carto import to_carto
        return to_carto(self, *args, **kwargs)

    def visualize(self, *args, **kwargs):
        from ..viz import Map, Layer
        return Map(Layer(self, *args, **kwargs))

    viz = visualize
