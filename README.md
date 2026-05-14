# PostalDataPI Python SDK

Official Python client for the [PostalDataPI](https://postaldatapi.com) global postal code API. Look up, validate, and search postal codes across 70+ countries with sub-10ms response times.

## Installation

```bash
pip install postaldatapi
```

## Quick Start

```python
from postaldatapi import PostalDataPI

client = PostalDataPI(api_key="your-api-key")

# Look up a US ZIP code
result = client.lookup("90210")
print(result.city)                # Beverly Hills
print(result.state_abbreviation)  # CA

# Look up a German postal code
result = client.lookup("10115", country="DE")
print(result.city)                # Berlin

# Validate a UK postcode
result = client.validate("SW1A", country="GB")
print(result.valid)               # True

# Search by city name
results = client.search_city("Beverly Hills", state="CA")
print(results.postal_codes)       # ['90209', '90210', '90211', ...]

# Get rich metadata
meta = client.metacode("90210")
print(meta.meta["county"])        # Los Angeles County
print(meta.meta["timezone"])      # America/Los_Angeles
print(meta.latitude)              # 34.1031
print(meta.longitude)             # -118.4163
```

## API Methods

### `client.lookup(postal_code, *, country="US")`

Returns city and state for a postal code.

### `client.validate(postal_code, *, country="US")`

Checks whether a postal code exists. Returns `ValidateResult` with `.valid` boolean.

### `client.search_city(city, *, state=None, country="US")`

Finds postal codes matching a city name. State is required for US queries.

### `client.metacode(postal_code, *, country="US")`

Returns rich metadata: coordinates, county (US), timezone (US), and all available data source fields.

(Available as of v0.3.0. The earlier name `client.metazip()` is preserved as a deprecated alias and emits a `DeprecationWarning` — both methods return identical data.)

## Country Support

Pass any ISO 3166-1 alpha-2 country code: `US`, `GB`, `DE`, `FR`, `CA`, `JP`, `AU`, and 60+ more. Country defaults to `US` if omitted.

## Error Handling

```python
from postaldatapi import PostalDataPI, NotFoundError, AuthenticationError

client = PostalDataPI(api_key="your-api-key")

try:
    result = client.lookup("00000")
except NotFoundError:
    print("Postal code not found")
except AuthenticationError:
    print("Invalid API key")
```

Exception classes: `AuthenticationError` (401), `NotFoundError` (404), `ValidationError` (400), `RateLimitError` (429), `InsufficientBalanceError` (402), `ServerError` (5xx).

## Configuration

```python
# Custom base URL (for staging or self-hosted)
client = PostalDataPI(
    api_key="your-key",
    base_url="https://staging.postaldatapi.com",
    timeout=30,  # seconds
)
```

## Account Balance

Every response includes your current account balance:

```python
result = client.lookup("90210")
print(f"Remaining balance: ${result.balance:.2f}")
```

## License

MIT
