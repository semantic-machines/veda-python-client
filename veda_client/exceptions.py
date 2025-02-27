"""
Exceptions for the Veda Platform API client.
"""


class VedaError(Exception):
    """Base exception for all Veda client errors."""
    pass


class VedaAuthError(VedaError):
    """Exception raised for authentication errors."""
    pass


class VedaRequestError(VedaError):
    """Exception raised for invalid requests."""
    pass


class VedaResponseError(VedaError):
    """Exception raised for errors in API responses."""
    pass


class VedaServerError(VedaError):
    """Exception raised for server errors."""
    pass
