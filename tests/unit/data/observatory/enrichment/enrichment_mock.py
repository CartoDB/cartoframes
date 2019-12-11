class CatalogEntityWithGeographyMock:
    def __init__(self, geography):
        self.geography = geography


class GeographyMock:
    def __init__(self, is_public_data=False):
        self.is_public_data = is_public_data
