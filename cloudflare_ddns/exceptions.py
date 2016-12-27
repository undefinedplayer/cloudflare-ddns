class CloudFlareError(Exception):
    """
    Base exception for CloudFlare module
    """
    pass


class ZoneNotFound(CloudFlareError):
    """
    Raised when a specified zone is not found from CloudFlare
    """
    pass


class RecordNotFound(CloudFlareError):
    """
    Raised when a specified record is not found for a zone from CloudFlare
    """
    pass
