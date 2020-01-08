
class DOError(Exception):
    """This exception is raised when a problem is encountered while using DO functions.

    """
    def __init__(self, message):
        super(DOError, self).__init__(message)


class CatalogError(DOError):
    """This exception is raised when a problem is encountered while using catalog functions.

    """
    def __init__(self, message):
        super(CatalogError, self).__init__(message)


class DiscoveryError(DOError):
    """This exception is raised when a problem is encountered while using the Catalog Discovery
    functions (i.e. requesting an element with an unknown ID).

    """
    def __init__(self, message):
        super(DiscoveryError, self).__init__(message)


class EnrichmentError(DOError):
    """This exception is raised when a problem is encountered while using enrichment functions.

    """
    def __init__(self, message):
        super(EnrichmentError, self).__init__(message)


class PublishError(Exception):
    """This exception is raised when a problem is encountered while publishing visualizations.

    """
    def __init__(self, message):
        super(PublishError, self).__init__(message)
