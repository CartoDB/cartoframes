from geopandas import GeoDataFrame


class CartoDataFrame(GeoDataFrame):

    def __init__(self, *args, **kwargs):
        super(CartoDataFrame, self).__init__(*args, **kwargs)
