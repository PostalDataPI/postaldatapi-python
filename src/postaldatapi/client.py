"""PostalDataPI client -- the main entry point for the SDK."""

from __future__ import annotations

from typing import Any, Dict, Optional

import requests

from postaldatapi.exceptions import (
    AuthenticationError,
    InsufficientBalanceError,
    NotFoundError,
    PostalDataPIError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from postaldatapi.models import (
    CitySearchResult,
    LookupResult,
    MetazipResult,
    RateLimit,
    RateLimitWindow,
    ValidateResult,
)

DEFAULT_BASE_URL = "https://postaldatapi.com"


class PostalDataPI:
    """Client for the PostalDataPI global postal code API.

    Args:
        api_key: Your PostalDataPI API key.
        base_url: API base URL. Override for staging or local development.
        timeout: Request timeout in seconds. Default: 10.

    Example::

        from postaldatapi import PostalDataPI

        client = PostalDataPI(api_key="your-api-key")

        # Lookup a US ZIP code
        result = client.lookup("90210")
        print(result.city, result.state_abbreviation)

        # Lookup a German postal code
        result = client.lookup("10115", country="DE")
        print(result.city)

        # Validate a UK postcode
        result = client.validate("SW1A", country="GB")
        print(result.valid)
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: int = 10,
    ):
        if not api_key:
            raise ValueError("api_key is required")
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._session = requests.Session()
        self._session.headers["Content-Type"] = "application/json"

    def lookup(self, postal_code: str, *, country: str = "US") -> LookupResult:
        """Look up city and state for a postal code.

        Args:
            postal_code: The postal code to look up.
            country: ISO 3166-1 alpha-2 country code. Default: "US".

        Returns:
            LookupResult with city, state, and balance info.

        Raises:
            NotFoundError: Postal code not found.
            AuthenticationError: Invalid API key.
            RateLimitError: Rate limit exceeded.
            InsufficientBalanceError: Account balance too low.
        """
        payload: Dict[str, Any] = {
            "zipcode": postal_code,
            "apiKey": self._api_key,
        }
        if country.upper() != "US":
            payload["country"] = country.upper()

        data = self._request("POST", "/api/lookup", payload)

        return LookupResult(
            city=data.get("city", ""),
            state=data.get("state", ""),
            state_abbreviation=data.get("ST", ""),
            balance=data.get("balance", 0.0),
            rate_limit=self._parse_rate_limit(data),
            raw=data,
        )

    def validate(self, postal_code: str, *, country: str = "US") -> ValidateResult:
        """Check whether a postal code exists.

        Args:
            postal_code: The postal code to validate.
            country: ISO 3166-1 alpha-2 country code. Default: "US".

        Returns:
            ValidateResult with valid flag and balance info.

        Raises:
            AuthenticationError: Invalid API key.
            RateLimitError: Rate limit exceeded.
            InsufficientBalanceError: Account balance too low.
        """
        payload: Dict[str, Any] = {
            "zipcode": postal_code,
            "apiKey": self._api_key,
        }
        if country.upper() != "US":
            payload["country"] = country.upper()

        data = self._request("POST", "/api/validate", payload)

        return ValidateResult(
            valid=data.get("valid", False),
            postal_code=data.get("zipcode", postal_code),
            balance=data.get("balance", 0.0),
            rate_limit=self._parse_rate_limit(data),
            raw=data,
        )

    def search_city(
        self,
        city: str,
        *,
        state: Optional[str] = None,
        country: str = "US",
    ) -> CitySearchResult:
        """Search for postal codes by city name.

        Args:
            city: City name to search for.
            state: State abbreviation (required for US, optional for other countries).
            country: ISO 3166-1 alpha-2 country code. Default: "US".

        Returns:
            CitySearchResult with matching postal codes and balance info.

        Raises:
            ValidationError: Missing required state for US queries.
            AuthenticationError: Invalid API key.
            RateLimitError: Rate limit exceeded.
            InsufficientBalanceError: Account balance too low.
        """
        payload: Dict[str, Any] = {
            "city": city,
            "apiKey": self._api_key,
        }
        if state:
            payload["ST"] = state
        if country.upper() != "US":
            payload["country"] = country.upper()

        data = self._request("POST", "/api/city", payload)

        return CitySearchResult(
            postal_codes=data.get("zipcodes", []),
            balance=data.get("balance", 0.0),
            rate_limit=self._parse_rate_limit(data),
            raw=data,
        )

    def metazip(self, postal_code: str, *, country: str = "US") -> MetazipResult:
        """Get rich metadata for a postal code.

        Returns detailed information including coordinates, county (US),
        timezone (US), and any additional metadata from the data source.

        Args:
            postal_code: The postal code to look up.
            country: ISO 3166-1 alpha-2 country code. Default: "US".

        Returns:
            MetazipResult with full metadata dict and convenience fields.

        Raises:
            NotFoundError: Postal code not found.
            AuthenticationError: Invalid API key.
            RateLimitError: Rate limit exceeded.
            InsufficientBalanceError: Account balance too low.
        """
        payload: Dict[str, Any] = {
            "zipcode": postal_code,
            "apiKey": self._api_key,
        }
        if country.upper() != "US":
            payload["country"] = country.upper()

        data = self._request("POST", "/api/metazip", payload)

        meta = data.get("meta", {})
        # US uses "city", non-US uses "placeName"
        city = meta.get("city", meta.get("placeName", ""))
        # US uses "zipcode", non-US uses "postalCode"
        code = meta.get("zipcode", meta.get("postalCode", postal_code))

        return MetazipResult(
            meta=meta,
            postal_code=code,
            city=city,
            latitude=meta.get("latitude"),
            longitude=meta.get("longitude"),
            balance=data.get("balance", 0.0),
            rate_limit=self._parse_rate_limit(data),
            raw=data,
        )

    # -- Internal helpers --

    def _request(self, method: str, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Make an API request and handle errors."""
        url = self._base_url + path

        try:
            response = self._session.request(
                method,
                url,
                json=payload,
                timeout=self._timeout,
            )
        except requests.ConnectionError as e:
            raise PostalDataPIError(f"Connection failed: {e}", status_code=0) from e
        except requests.Timeout as e:
            raise PostalDataPIError(f"Request timed out after {self._timeout}s", status_code=0) from e

        if response.status_code == 200:
            return response.json()

        # Parse error response
        try:
            error_data = response.json()
            message = error_data.get("error", response.text)
        except (ValueError, KeyError):
            message = response.text or f"HTTP {response.status_code}"

        status = response.status_code

        if status == 400:
            raise ValidationError(message, status)
        elif status == 401:
            raise AuthenticationError(message, status)
        elif status == 402:
            raise InsufficientBalanceError(message, status)
        elif status == 404:
            raise NotFoundError(message, status)
        elif status == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(
                message,
                status,
                retry_after=int(retry_after) if retry_after else None,
            )
        elif status >= 500:
            raise ServerError(message, status)
        else:
            raise PostalDataPIError(message, status)

    @staticmethod
    def _parse_rate_limit(data: Dict[str, Any]) -> RateLimit:
        """Parse rate limit info from API response."""
        rl = data.get("rateLimit")
        if not rl:
            return RateLimit()

        def parse_window(w: Optional[Dict[str, Any]]) -> RateLimitWindow:
            if not w:
                return RateLimitWindow()
            return RateLimitWindow(
                limit=w.get("limit"),
                current=w.get("current"),
                approaching_limit=w.get("approachingLimit", False),
            )

        return RateLimit(
            enabled=rl.get("enabled", False),
            per_minute=parse_window(rl.get("perMinute")),
            per_hour=parse_window(rl.get("perHour")),
            per_day=parse_window(rl.get("perDay")),
        )
