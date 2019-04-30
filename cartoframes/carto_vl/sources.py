from .source.dataset import Dataset
from .source.sql import SQL
from .source.geojson import GeoJSON


class Sources():
    Dataset = Dataset
    SQL = SQL
    GeoJSON = GeoJSON
