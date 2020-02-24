class BaseSource:
    """BaseSource"""

    def get_credentials(self):
        return None

    def get_geom_type(self):
        return None

    def compute_metadata(self, columns=None):
        return None

    def is_local(self):
        return False

    def is_public(self):
        return False

    def schema(self):
        return None

    def get_table_names(self):
        return []

    def get_datetime_column_names(self):
        return None
