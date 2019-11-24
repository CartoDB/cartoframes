from geopandas import GeoDataFrame

from ..utils.geom_utils import generate_index, generate_geometry


class CartoDataFrame(GeoDataFrame):

    def __init__(self, *args, **kwargs):
        super(CartoDataFrame, self).__init__(*args, **kwargs)

    @staticmethod
    def from_carto(*args, **kwargs):
        from ..io.carto import read_carto
        return read_carto(*args, **kwargs)

    @classmethod
    def from_file(cls, filename, **kwargs):
        gdf = GeoDataFrame.from_file(filename, **kwargs)
        return cls(gdf)

    @property
    def _constructor(self):
        return CartoDataFrame
        
    @classmethod
    def from_features(cls, features, **kwargs):
        gdf = GeoDataFrame.from_features(features, **kwargs)
        return cls(gdf)

    def to_carto(self, *args, **kwargs):
        from ..io.carto import to_carto
        return to_carto(self, *args, **kwargs)

    def convert(self, index_column=None, geom_column=None, lnglat_columns=None,
                drop_index=True, drop_geom=True, drop_lnglat=True):
        # Magic function
        generate_index(self, index_column, drop_index)
        generate_geometry(self, geom_column, lnglat_columns, drop_geom, drop_lnglat)
        return self

    def viz(self, *args, **kwargs):
        from ..viz import Map, Layer
        return Map(Layer(self, *args, **kwargs))
