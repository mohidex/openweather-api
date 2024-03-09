class UnauthorizedError(Exception):
    """Exception raised when the API request is unauthorized."""
    pass


class NotFoundError(Exception):
    """Exception raised when the requested resource is not found."""
    pass


class TooManyRequestError(Exception):
    """Exception raised when there are too many requests in a given time frame."""
    pass


class UnexpectedError(Exception):
    """Exception raised when an unexpected error occurs during the API request."""
    pass


class InvalidResponse(Exception):
    """Exception raised when got missing/corrupted data during successful API request."""
    pass
