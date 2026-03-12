from typing import Dict, Optional, Any

import requests

from .exceptions import PostalDataAPIError

DEFAULT_BASE_URL = "https://postaldatapi.com/api"


class PostalDataPI:
    """Client for the PostalDataPI postal code API.

    Args:
        api_key: Your PostalDataPI API key.
        base_url: API base URL. Defaults to https://postaldatapi.com/api.
            The alias https://zipdatapi.com/api resolves to the same backend.
    """

    def __init__(self, api_key: str, base_url: str = DEFAULT_BASE_URL):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self._session = requests.Session()
        self._session.headers.update({"Content-Type": "application/json"})

    def _post(self, endpoint: str, body: Dict[str, Any]) -> dict:
        body["apiKey"] = self.api_key
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        resp = self._session.post(url, json=body, timeout=30)
        try:
            data = resp.json()
        except ValueError:
            data = {"error": resp.text}
        if not resp.ok:
            message = data.get("error") or data.get("message") or resp.reason
            raise PostalDataAPIError(
                message=message,
                status_code=resp.status_code,
                response=data,
            )
        return data

    def lookup(self, postal_code: str, country: Optional[str] = None) -> dict:
        """Look up data for a postal code.

        Args:
            postal_code: The postal code to look up (e.g. "90210").
            country: ISO 3166-1 alpha-2 country code (e.g. "US"). Defaults to US.

        Returns:
            dict: Postal code data including place name, lat/lon, and more.
        """
        body: Dict[str, Any] = {"zipCode": postal_code}
        if country is not None:
            body["country"] = country
        return self._post("lookup", body)

    def validate(self, postal_code: str, country: Optional[str] = None) -> dict:
        """Validate a postal code.

        Args:
            postal_code: The postal code to validate.
            country: ISO 3166-1 alpha-2 country code. Defaults to US.

        Returns:
            dict: Validation result including a ``valid`` boolean field.
        """
        body: Dict[str, Any] = {"zipCode": postal_code}
        if country is not None:
            body["country"] = country
        return self._post("validate", body)

    def city_search(
        self,
        city: str,
        state: Optional[str] = None,
        country: Optional[str] = None,
    ) -> dict:
        """Find postal codes for a city.

        Args:
            city: City name to search for.
            state: State or region code (e.g. "CA"). Optional.
            country: ISO 3166-1 alpha-2 country code. Defaults to US.

        Returns:
            dict: Matching postal codes for the city.
        """
        body: Dict[str, Any] = {"city": city}
        if state is not None:
            body["state"] = state
        if country is not None:
            body["country"] = country
        return self._post("city", body)

    def metazip(self, postal_code: str, country: Optional[str] = None) -> dict:
        """Retrieve enriched metadata for a postal code.

        Args:
            postal_code: The postal code to enrich.
            country: ISO 3166-1 alpha-2 country code. Defaults to US.

        Returns:
            dict: Enriched postal code metadata.
        """
        body: Dict[str, Any] = {"zipCode": postal_code}
        if country is not None:
            body["country"] = country
        return self._post("metazip", body)

    def about(self) -> dict:
        """Retrieve API info and health status.

        Returns:
            dict: API version, health status, and account information.
        """
        return self._post("aboutapi", {})
