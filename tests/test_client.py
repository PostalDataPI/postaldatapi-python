"""Tests for the PostalDataPI Python SDK.

These tests run against a live API server. Set environment variables:
    TEST_BASE_URL: API base URL (default: http://localhost:3000)
    TEST_API_KEY: A valid API key for the test server

To run: pytest tests/ -v
"""

import os

import pytest

from postaldatapi import (
    PostalDataPI,
    BulkValidateRecord,
    BulkValidateResult,
    LookupResult,
    ValidateResult,
    CitySearchResult,
    MetazipResult,
    AuthenticationError,
    NotFoundError,
    ValidationError,
)

BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:3000")
API_KEY = os.getenv("TEST_API_KEY", "")


def requires_api_key(func):
    """Skip test if no API key is available."""
    return pytest.mark.skipif(not API_KEY, reason="TEST_API_KEY not set")(func)


def client() -> PostalDataPI:
    return PostalDataPI(api_key=API_KEY, base_url=BASE_URL)


# -- Constructor tests (no API key needed) --

class TestConstructor:
    def test_requires_api_key(self):
        with pytest.raises(ValueError, match="api_key is required"):
            PostalDataPI(api_key="")

    def test_custom_base_url(self):
        c = PostalDataPI(api_key="test", base_url="https://custom.example.com/")
        assert c._base_url == "https://custom.example.com"

    def test_default_timeout(self):
        c = PostalDataPI(api_key="test")
        assert c._timeout == 10

    def test_custom_timeout(self):
        c = PostalDataPI(api_key="test", timeout=30)
        assert c._timeout == 30


# -- Authentication tests --

class TestAuthentication:
    def test_invalid_api_key(self):
        c = PostalDataPI(api_key="invalid-key", base_url=BASE_URL)
        with pytest.raises(AuthenticationError) as exc_info:
            c.lookup("90210")
        assert exc_info.value.status_code == 401

    def test_invalid_api_key_message(self):
        c = PostalDataPI(api_key="invalid-key", base_url=BASE_URL)
        with pytest.raises(AuthenticationError, match="Invalid API key"):
            c.lookup("90210")


# -- Lookup tests --

class TestLookup:
    @requires_api_key
    def test_us_lookup(self):
        result = client().lookup("90210")
        assert isinstance(result, LookupResult)
        assert result.city == "Beverly Hills"
        assert result.state == "California"
        assert result.state_abbreviation == "CA"
        assert result.balance > 0

    @requires_api_key
    def test_non_us_lookup(self):
        result = client().lookup("10115", country="DE")
        assert isinstance(result, LookupResult)
        assert result.city == "Berlin"

    @requires_api_key
    def test_country_case_insensitive(self):
        result = client().lookup("10115", country="de")
        assert result.city == "Berlin"

    @requires_api_key
    def test_not_found(self):
        with pytest.raises(NotFoundError) as exc_info:
            client().lookup("00000")
        assert exc_info.value.status_code == 404

    @requires_api_key
    def test_raw_response_included(self):
        result = client().lookup("90210")
        assert "city" in result.raw
        assert "performance" in result.raw

    @requires_api_key
    def test_rate_limit_in_response(self):
        result = client().lookup("90210")
        assert result.rate_limit is not None
        assert isinstance(result.rate_limit.enabled, bool)


# -- Validate tests --

class TestValidate:
    @requires_api_key
    def test_valid_us_zipcode(self):
        result = client().validate("90210")
        assert isinstance(result, ValidateResult)
        assert result.valid is True
        assert result.postal_code == "90210"

    @requires_api_key
    def test_invalid_us_zipcode(self):
        result = client().validate("00000")
        assert result.valid is False

    @requires_api_key
    def test_valid_non_us(self):
        result = client().validate("SW1A", country="GB")
        assert result.valid is True

    @requires_api_key
    def test_valid_germany(self):
        result = client().validate("10115", country="DE")
        assert result.valid is True


# -- City search tests --

class TestCitySearch:
    @requires_api_key
    def test_us_city_search(self):
        result = client().search_city("Beverly Hills", state="CA")
        assert isinstance(result, CitySearchResult)
        assert "90210" in result.postal_codes
        assert len(result.postal_codes) > 0

    @requires_api_key
    def test_non_us_city_search(self):
        result = client().search_city("Berlin", country="DE")
        assert isinstance(result, CitySearchResult)
        assert len(result.postal_codes) > 0

    @requires_api_key
    def test_us_city_requires_state(self):
        with pytest.raises(ValidationError):
            client().search_city("Beverly Hills")


# -- Metacode / Metazip tests --

class TestMetacode:
    """Tests for the new canonical method name (added in v0.3.0)."""

    @requires_api_key
    def test_us_metacode(self):
        result = client().metacode("90210")
        assert isinstance(result, MetazipResult)
        assert result.city == "Beverly Hills"
        assert result.postal_code == "90210"
        assert result.latitude is not None
        assert result.longitude is not None
        assert "county" in result.meta
        assert "timezone" in result.meta

    @requires_api_key
    def test_non_us_metacode(self):
        result = client().metacode("10115", country="DE")
        assert isinstance(result, MetazipResult)
        assert result.city == "Berlin"
        assert result.latitude is not None
        assert result.longitude is not None

    @requires_api_key
    def test_meta_dict_accessible(self):
        result = client().metacode("90210")
        assert isinstance(result.meta, dict)
        assert result.meta["state"] == "California"


class TestMetazipAlias:
    """Tests for the deprecated alias preserved for backward compatibility."""

    @requires_api_key
    def test_metazip_alias_still_works(self):
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            result = client().metazip("90210")
        assert isinstance(result, MetazipResult)
        assert result.city == "Beverly Hills"

    @requires_api_key
    def test_metazip_emits_deprecation_warning(self):
        import warnings
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always", DeprecationWarning)
            client().metazip("90210")
        deprecations = [w for w in caught if issubclass(w.category, DeprecationWarning)]
        assert len(deprecations) >= 1
        assert "metacode" in str(deprecations[0].message).lower()


class TestBulkValidate:
    @requires_api_key
    def test_bulk_validate_us_records(self):
        result = client().validate_bulk([
            {"postal_code": "90210", "country_code": "US"},
            {"postal_code": "10001", "country_code": "US"},
        ])
        assert isinstance(result, BulkValidateResult)
        assert len(result.results) == 2
        for r in result.results:
            assert isinstance(r, BulkValidateRecord)
            assert r.valid is True
            assert r.normalized is not None
            assert r.reason is None

    @requires_api_key
    def test_bulk_validate_mixed_country(self):
        result = client().validate_bulk([
            {"postal_code": "90210", "country_code": "US"},
            {"postal_code": "SW1A 1AA", "country_code": "GB"},
        ])
        assert len(result.results) == 2
        # GB outcode normalization
        assert result.results[1].normalized == "SW1A"

    @requires_api_key
    def test_bulk_validate_per_record_reasons(self):
        result = client().validate_bulk([
            {"postal_code": "90210", "country_code": "US"},
            {"postal_code": "FOO99", "country_code": "US"},
            {"postal_code": "12345", "country_code": "ZZ"},
        ])
        assert result.results[0].valid is True
        assert result.results[1].valid is False
        assert result.results[1].reason == "not_found"
        assert result.results[2].valid is False
        assert result.results[2].reason == "unknown_country"

    @requires_api_key
    def test_bulk_validate_total_cost_and_balance(self):
        result = client().validate_bulk([
            {"postal_code": "90210", "country_code": "US"},
        ])
        assert result.total_cost > 0
        assert isinstance(result.balance, (int, float))

    @requires_api_key
    def test_bulk_validate_accepts_camel_case_keys(self):
        # Tolerate JS-style keys for ergonomic JSON copy-paste
        result = client().validate_bulk([
            {"postalCode": "90210", "countryCode": "US"},
        ])
        assert result.results[0].valid is True

    @requires_api_key
    def test_bulk_validate_accepts_tuple_records(self):
        result = client().validate_bulk([("90210", "US"), ("10001", "US")])
        assert len(result.results) == 2
        assert all(r.valid for r in result.results)

    @requires_api_key
    def test_bulk_validate_empty_records_raises(self):
        with pytest.raises(ValidationError):
            client().validate_bulk([])

    def test_bulk_validate_record_missing_fields_raises(self):
        with pytest.raises(ValueError):
            client().validate_bulk([{"postal_code": "90210"}])  # no country_code
