from geopandas import GeoDataFrame

from ..utils.geom_utils import generate_index, generate_geometry


class CartoDataFrame(GeoDataFrame):

    def __init__(self, *args, **kwargs):
        index_column = kwargs.pop('index_column', None)
        geom_column = kwargs.pop('geom_column', None)
        lnglat_column = kwargs.pop('lnglat_column', None)
        keep_index = kwargs.pop('keep_index', False)
        keep_geom = kwargs.pop('keep_geom', False)
        keep_lnglat = kwargs.pop('keep_lnglat', False)

        super(CartoDataFrame, self).__init__(*args, **kwargs)

        generate_index(self, index_column, keep_index)
        generate_geometry(self, geom_column, lnglat_column, keep_geom, keep_lnglat)

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

    def to_carto(*args, **kwargs):
        from ..io.carto import to_carto
        return to_carto(*args, **kwargs)

    def render(self, *args, **kwargs):
        from ..viz import Map, Layer
        return Map(Layer(self, *args, **kwargs))
