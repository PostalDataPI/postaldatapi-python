"""Unit tests for the PostalDataPI client.

All HTTP calls are mocked via requests-mock; no network access required.
"""

import pytest
import requests_mock as requests_mock_module

from postaldatapi import PostalDataPI, PostalDataAPIError

API_KEY = "test-api-key-abc123"
BASE_URL = "https://postaldatapi.com/api"


@pytest.fixture
def client():
    return PostalDataPI(api_key=API_KEY)


@pytest.fixture
def mock_adapter():
    with requests_mock_module.Mocker() as m:
        yield m


# ---------------------------------------------------------------------------
# lookup
# ---------------------------------------------------------------------------

class TestLookup:
    def test_lookup_us_postal_code(self, client, mock_adapter):
        payload = {
            "postal_code": "90210",
            "place_name": "Beverly Hills",
            "latitude": 34.09,
            "longitude": -118.41,
        }
        mock_adapter.post(f"{BASE_URL}/lookup", json=payload)
        result = client.lookup("90210")
        assert result["postal_code"] == "90210"
        assert result["place_name"] == "Beverly Hills"

    def test_lookup_sends_api_key(self, client, mock_adapter):
        mock_adapter.post(f"{BASE_URL}/lookup", json={"postal_code": "90210"})
        client.lookup("90210")
        body = mock_adapter.last_request.json()
        assert body["apiKey"] == API_KEY

    def test_lookup_with_country(self, client, mock_adapter):
        payload = {"postal_code": "SW1A", "place_name": "Westminster"}
        mock_adapter.post(f"{BASE_URL}/lookup", json=payload)
        result = client.lookup("SW1A", country="GB")
        body = mock_adapter.last_request.json()
        assert body["country"] == "GB"
        assert body["zipCode"] == "SW1A"

    def test_lookup_without_country_omits_field(self, client, mock_adapter):
        mock_adapter.post(f"{BASE_URL}/lookup", json={})
        client.lookup("90210")
        body = mock_adapter.last_request.json()
        assert "country" not in body

    def test_lookup_raises_on_error(self, client, mock_adapter):
        mock_adapter.post(f"{BASE_URL}/lookup", json={"error": "Invalid API key"}, status_code=401)
        with pytest.raises(PostalDataAPIError) as exc_info:
            client.lookup("00000")
        assert exc_info.value.status_code == 401
        assert "Invalid API key" in exc_info.value.message


# ---------------------------------------------------------------------------
# validate
# ---------------------------------------------------------------------------

class TestValidate:
    def test_validate_returns_valid_true(self, client, mock_adapter):
        mock_adapter.post(f"{BASE_URL}/validate", json={"valid": True, "postal_code": "90210"})
        result = client.validate("90210")
        assert result["valid"] is True

    def test_validate_returns_valid_false(self, client, mock_adapter):
        mock_adapter.post(f"{BASE_URL}/validate", json={"valid": False})
        result = client.validate("00000")
        assert result["valid"] is False

    def test_validate_with_country(self, client, mock_adapter):
        mock_adapter.post(f"{BASE_URL}/validate", json={"valid": True})
        client.validate("T2P", country="CA")
        body = mock_adapter.last_request.json()
        assert body["country"] == "CA"
        assert body["zipCode"] == "T2P"

    def test_validate_raises_on_server_error(self, client, mock_adapter):
        mock_adapter.post(f"{BASE_URL}/validate", json={"error": "Internal error"}, status_code=500)
        with pytest.raises(PostalDataAPIError) as exc_info:
            client.validate("90210")
        assert exc_info.value.status_code == 500


# ---------------------------------------------------------------------------
# city_search
# ---------------------------------------------------------------------------

class TestCitySearch:
    def test_city_search_basic(self, client, mock_adapter):
        payload = {"results": [{"postal_code": "90210", "place_name": "Beverly Hills"}]}
        mock_adapter.post(f"{BASE_URL}/city", json=payload)
        result = client.city_search("Beverly Hills")
        assert len(result["results"]) == 1

    def test_city_search_with_state(self, client, mock_adapter):
        mock_adapter.post(f"{BASE_URL}/city", json={"results": []})
        client.city_search("Beverly Hills", state="CA")
        body = mock_adapter.last_request.json()
        assert body["city"] == "Beverly Hills"
        assert body["state"] == "CA"

    def test_city_search_with_country(self, client, mock_adapter):
        mock_adapter.post(f"{BASE_URL}/city", json={"results": []})
        client.city_search("Munich", country="DE")
        body = mock_adapter.last_request.json()
        assert body["country"] == "DE"
        assert "state" not in body

    def test_city_search_all_params(self, client, mock_adapter):
        mock_adapter.post(f"{BASE_URL}/city", json={"results": []})
        client.city_search("Springfield", state="IL", country="US")
        body = mock_adapter.last_request.json()
        assert body["city"] == "Springfield"
        assert body["state"] == "IL"
        assert body["country"] == "US"

    def test_city_search_raises_on_not_found(self, client, mock_adapter):
        mock_adapter.post(f"{BASE_URL}/city", json={"error": "Not found"}, status_code=404)
        with pytest.raises(PostalDataAPIError) as exc_info:
            client.city_search("Atlantis")
        assert exc_info.value.status_code == 404


# ---------------------------------------------------------------------------
# metazip
# ---------------------------------------------------------------------------

class TestMetazip:
    def test_metazip_returns_enriched_data(self, client, mock_adapter):
        payload = {
            "postal_code": "90210",
            "place_name": "Beverly Hills",
            "county": "Los Angeles",
            "timezone": "America/Los_Angeles",
        }
        mock_adapter.post(f"{BASE_URL}/metazip", json=payload)
        result = client.metazip("90210")
        assert result["county"] == "Los Angeles"
        assert result["timezone"] == "America/Los_Angeles"

    def test_metazip_with_country(self, client, mock_adapter):
        mock_adapter.post(f"{BASE_URL}/metazip", json={})
        client.metazip("10115", country="DE")
        body = mock_adapter.last_request.json()
        assert body["zipCode"] == "10115"
        assert body["country"] == "DE"

    def test_metazip_raises_on_error(self, client, mock_adapter):
        mock_adapter.post(f"{BASE_URL}/metazip", json={"error": "Forbidden"}, status_code=403)
        with pytest.raises(PostalDataAPIError) as exc_info:
            client.metazip("90210")
        assert exc_info.value.status_code == 403


# ---------------------------------------------------------------------------
# about
# ---------------------------------------------------------------------------

class TestAbout:
    def test_about_returns_api_info(self, client, mock_adapter):
        payload = {"version": "1.0.0", "status": "healthy"}
        mock_adapter.post(f"{BASE_URL}/aboutapi", json=payload)
        result = client.about()
        assert result["status"] == "healthy"

    def test_about_sends_only_api_key(self, client, mock_adapter):
        mock_adapter.post(f"{BASE_URL}/aboutapi", json={})
        client.about()
        body = mock_adapter.last_request.json()
        assert set(body.keys()) == {"apiKey"}
        assert body["apiKey"] == API_KEY


# ---------------------------------------------------------------------------
# PostalDataAPIError
# ---------------------------------------------------------------------------

class TestPostalDataAPIError:
    def test_error_attributes(self, client, mock_adapter):
        mock_adapter.post(f"{BASE_URL}/lookup", json={"error": "Bad request"}, status_code=400)
        with pytest.raises(PostalDataAPIError) as exc_info:
            client.lookup("bad")
        err = exc_info.value
        assert err.status_code == 400
        assert err.message == "Bad request"
        assert err.response == {"error": "Bad request"}

    def test_error_repr(self):
        err = PostalDataAPIError("Not found", 404, {"error": "Not found"})
        assert "404" in repr(err)
        assert "Not found" in repr(err)


# ---------------------------------------------------------------------------
# Custom base URL
# ---------------------------------------------------------------------------

class TestCustomBaseUrl:
    def test_alias_base_url(self, mock_adapter):
        alias_base = "https://zipdatapi.com/api"
        client = PostalDataPI(api_key=API_KEY, base_url=alias_base)
        mock_adapter.post(f"{alias_base}/lookup", json={"postal_code": "90210"})
        result = client.lookup("90210")
        assert result["postal_code"] == "90210"

    def test_trailing_slash_stripped(self, mock_adapter):
        client = PostalDataPI(api_key=API_KEY, base_url=f"{BASE_URL}/")
        mock_adapter.post(f"{BASE_URL}/lookup", json={})
        client.lookup("90210")  # should not double-slash
