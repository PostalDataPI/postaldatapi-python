"""Exception classes for PostalDataPI SDK."""


class PostalDataPIError(Exception):
    """Base exception for all PostalDataPI errors."""

    def __init__(self, message: str, status_code: int = 0):
        super().__init__(message)
        self.status_code = status_code


class AuthenticationError(PostalDataPIError):
    """Raised when the API key is missing or invalid (HTTP 401)."""
    pass


class NotFoundError(PostalDataPIError):
    """Raised when a postal code is not found (HTTP 404)."""
    pass


class ValidationError(PostalDataPIError):
    """Raised when the request is malformed (HTTP 400)."""
    pass


class RateLimitError(PostalDataPIError):
    """Raised when rate limits are exceeded (HTTP 429).

    Attributes:
        retry_after: Seconds to wait before retrying (from Retry-After header).
    """

    def __init__(self, message: str, status_code: int = 429, retry_after: int | None = None):
        super().__init__(message, status_code)
        self.retry_after = retry_after


class InsufficientBalanceError(PostalDataPIError):
    """Raised when account balance is too low (HTTP 402)."""
    pass


class ServerError(PostalDataPIError):
    """Raised for unexpected server errors (HTTP 5xx)."""
    pass
