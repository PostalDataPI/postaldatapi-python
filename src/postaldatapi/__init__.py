"""PostalDataPI Python SDK -- Global postal code validation and enrichment."""

from postaldatapi.client import PostalDataPI
from postaldatapi.models import (
    LookupResult,
    ValidateResult,
    CitySearchResult,
    MetazipResult,
    RateLimit,
    RateLimitWindow,
)
from postaldatapi.exceptions import (
    PostalDataPIError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    InsufficientBalanceError,
    ValidationError,
    ServerError,
)

__version__ = "0.1.0"

__all__ = [
    "PostalDataPI",
    "LookupResult",
    "ValidateResult",
    "CitySearchResult",
    "MetazipResult",
    "RateLimit",
    "RateLimitWindow",
    "PostalDataPIError",
    "AuthenticationError",
    "NotFoundError",
    "RateLimitError",
    "InsufficientBalanceError",
    "ValidationError",
    "ServerError",
]
