"""Response models for PostalDataPI SDK.

All models use dataclasses for zero additional dependencies.
Fields are typed to match the API response format exactly.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class RateLimitWindow:
    """Rate limit status for a single time window (per-minute, per-hour, per-day)."""
    limit: Optional[int] = None
    current: Optional[int] = None
    approaching_limit: bool = False


@dataclass
class RateLimit:
    """Rate limit status across all time windows."""
    enabled: bool = False
    per_minute: RateLimitWindow = field(default_factory=RateLimitWindow)
    per_hour: RateLimitWindow = field(default_factory=RateLimitWindow)
    per_day: RateLimitWindow = field(default_factory=RateLimitWindow)


@dataclass
class LookupResult:
    """Result from a postal code lookup.

    Attributes:
        city: City or place name associated with the postal code.
        state: Full state/region name (may be empty for non-US countries).
        state_abbreviation: State abbreviation, e.g. "CA" (may be empty for non-US).
        balance: Remaining account balance in USD.
        rate_limit: Current rate limit status.
        raw: The complete raw API response dict.
    """
    city: str
    state: str
    state_abbreviation: str
    balance: float
    rate_limit: RateLimit = field(default_factory=RateLimit)
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)


@dataclass
class ValidateResult:
    """Result from postal code validation.

    Attributes:
        valid: Whether the postal code exists in the database.
        postal_code: The postal code that was validated.
        balance: Remaining account balance in USD.
        rate_limit: Current rate limit status.
        raw: The complete raw API response dict.
    """
    valid: bool
    postal_code: str
    balance: float
    rate_limit: RateLimit = field(default_factory=RateLimit)
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)


@dataclass
class CitySearchResult:
    """Result from a city search.

    Attributes:
        postal_codes: List of postal codes matching the city search.
        balance: Remaining account balance in USD.
        rate_limit: Current rate limit status.
        raw: The complete raw API response dict.
    """
    postal_codes: List[str]
    balance: float
    rate_limit: RateLimit = field(default_factory=RateLimit)
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)


@dataclass
class MetazipResult:
    """Result from a metazip (rich metadata) lookup.

    For US postal codes, includes county, timezone, and full state info.
    For non-US postal codes, includes whatever metadata the data source provides.

    Attributes:
        meta: Dict of all metadata fields returned by the API.
        postal_code: The queried postal code.
        city: City/place name (extracted from meta for convenience).
        latitude: Latitude coordinate (extracted from meta for convenience).
        longitude: Longitude coordinate (extracted from meta for convenience).
        balance: Remaining account balance in USD.
        rate_limit: Current rate limit status.
        raw: The complete raw API response dict.
    """
    meta: Dict[str, Any]
    postal_code: str
    city: str
    latitude: Optional[float]
    longitude: Optional[float]
    balance: float
    rate_limit: RateLimit = field(default_factory=RateLimit)
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)
