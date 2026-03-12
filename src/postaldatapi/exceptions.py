class PostalDataAPIError(Exception):
    """Raised when the PostalDataPI API returns a non-2xx response."""

    def __init__(self, message: str, status_code: int, response: dict):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response = response

    def __repr__(self) -> str:
        return f"PostalDataAPIError(status_code={self.status_code}, message={self.message!r})"
