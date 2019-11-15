from geopandas import GeoDataFrame


class CartoDataFrame(GeoDataFrame):

    def __init__(self, *args, **kwargs):
        super(CartoDataFrame, self).__init__(*args, **kwargs)

    @staticmethod
    def from_carto(*args, **kwargs):
        from ..io.carto import read_carto
        return read_carto(*args, **kwargs)

    def render(self):
        from ..viz import Map, Layer
        return Map(Layer(self))
