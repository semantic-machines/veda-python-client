"""
Veda Platform Python Client

A client library for interacting with the Veda Platform HTTP API.
"""

from .client import VedaClient
from .exceptions import (
    VedaError,
    VedaAuthError,
    VedaRequestError,
    VedaResponseError,
    VedaServerError
)
from .models import Individual

__version__ = "0.1.0"
