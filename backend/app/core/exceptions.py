class ConcurrencyException(Exception):
    """Raised when an optimistic locking conflict occurs."""
    pass

class BookNotAvailableException(Exception):
    """Raised when a book copy is not available for loan."""
    pass

class AuthException(Exception):
    """Base exception for authentication errors."""
    pass

class MissingTokenException(AuthException):
    pass

class InvalidTokenException(AuthException):
    pass

class ExpiredTokenException(AuthException):
    pass

class AdminAccessRequiredException(AuthException):
    pass