
class DiscoveryError(Exception):
    """This exception is raised when a problem is encountered while using the Catalog Discovery functions (i.e. requesting
    an element with an unknown ID).

    """
    def __init__(self, message):
        super(DiscoveryError, self).__init__(message)


class EnrichmentError(Exception):
    """This exception is raised when a problem is encountered while using enrichment functions.

    """
    def __init__(self, message):
        super(EnrichmentError, self).__init__(message)
