"""PostalDataPI Python SDK -- Global postal code validation and enrichment."""

from postaldatapi.client import PostalDataPI
from postaldatapi.models import (
    BulkValidateRecord,
    BulkValidateResult,
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

__version__ = "0.2.0"

__all__ = [
    "PostalDataPI",
    "BulkValidateRecord",
    "BulkValidateResult",
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
