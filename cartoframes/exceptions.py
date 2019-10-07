from __future__ import absolute_import


class DiscoveryException(Exception):
    """
    This exception is raised when a problem is encountered while using the Catalog Discovery functions (i.e. requesting
    an element with an unknown ID).
    """

    def __init__(self, message):
        super(DiscoveryException, self).__init__(message)


class EnrichmentException(Exception):
    """
    This exception is raised when a problem is encountered while using enrichment functions.
    """

    def __init__(self, message):
        super(EnrichmentException, self).__init__(message)
