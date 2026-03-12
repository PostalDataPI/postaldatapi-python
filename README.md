# postaldatapi

![PyPI version](https://img.shields.io/pypi/v/postaldatapi)
![Python versions](https://img.shields.io/pypi/pyversions/postaldatapi)
![License](https://img.shields.io/pypi/l/postaldatapi)

Python client for the [PostalDataPI](https://postaldatapi.com) global postal code API.

Look up postal codes, validate addresses, search cities, and retrieve enriched metadata for 200+ countries.

---

## Installation

```bash
pip install postaldatapi
```

Requires Python 3.8+.

---

## Quick Start

```python
from postaldatapi import PostalDataPI

client = PostalDataPI(api_key="your-api-key")

result = client.lookup("90210", country="US")
print(result)
# {"postal_code": "90210", "place_name": "Beverly Hills", "latitude": 34.09, "longitude": -118.41, ...}
```

---

## Methods

All methods return a `dict` parsed from the API JSON response.
All methods raise `PostalDataAPIError` on non-2xx responses.

### `lookup(postal_code, country=None)`

Look up data for a postal code.

```python
result = client.lookup("90210")
result = client.lookup("SW1A", country="GB")
result = client.lookup("10115", country="DE")
```

**Parameters:**
- `postal_code` (str) — The postal code to look up.
- `country` (str, optional) — ISO 3166-1 alpha-2 country code. Defaults to `"US"`.

---

### `validate(postal_code, country=None)`

Validate whether a postal code exists.

```python
result = client.validate("90210")
if result["valid"]:
    print("Valid postal code")
```

**Parameters:**
- `postal_code` (str) — The postal code to validate.
- `country` (str, optional) — ISO 3166-1 alpha-2 country code. Defaults to `"US"`.

---

### `city_search(city, state=None, country=None)`

Find postal codes for a city.

```python
result = client.city_search("Beverly Hills", state="CA", country="US")
result = client.city_search("Munich", country="DE")
```

**Parameters:**
- `city` (str) — City name to search.
- `state` (str, optional) — State or region code (e.g. `"CA"`).
- `country` (str, optional) — ISO 3166-1 alpha-2 country code. Defaults to `"US"`.

---

### `metazip(postal_code, country=None)`

Retrieve enriched metadata for a postal code, including county, timezone, and confidence data.

```python
result = client.metazip("90210", country="US")
print(result["timezone"])
```

**Parameters:**
- `postal_code` (str) — The postal code to enrich.
- `country` (str, optional) — ISO 3166-1 alpha-2 country code. Defaults to `"US"`.

---

### `about()`

Retrieve API info, version, and health status.

```python
info = client.about()
print(info["status"])
```

---

## Error Handling

```python
from postaldatapi import PostalDataPI, PostalDataAPIError

client = PostalDataPI(api_key="your-api-key")

try:
    result = client.lookup("invalid-code")
except PostalDataAPIError as e:
    print(f"API error {e.status_code}: {e.message}")
    print(e.response)  # full response dict
```

`PostalDataAPIError` attributes:
- `status_code` (int) — HTTP status code returned by the API.
- `message` (str) — Error message from the API response.
- `response` (dict) — Full parsed response body.

---

## Custom Base URL

The `https://zipdatapi.com/api` domain resolves to the same backend:

```python
client = PostalDataPI(api_key="your-api-key", base_url="https://zipdatapi.com/api")
```

---

## API Keys

Sign up at [postaldatapi.com](https://postaldatapi.com) to get an API key. New accounts include 1,000 free queries.

---

## Links

- Full API documentation: [https://postaldatapi.com/docs](https://postaldatapi.com/docs)
- GitHub: [https://github.com/PostalDataPI/postaldatapi-python](https://github.com/PostalDataPI/postaldatapi-python)
- PyPI: [https://pypi.org/project/postaldatapi](https://pypi.org/project/postaldatapi)

---

## License

MIT. See [LICENSE](LICENSE).
