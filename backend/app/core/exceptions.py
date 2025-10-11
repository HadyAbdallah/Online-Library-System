"""
Defines custom exception classes for the application.
"""
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
    """Raised when the Authorization header is missing."""
    pass

class InvalidTokenException(AuthException):
    """Raised when a token is invalid, malformed, or revoked."""
    pass

class ExpiredTokenException(AuthException):
    """Raised when a token's expiration time has passed."""
    pass

class AdminAccessRequiredException(AuthException):
    """Raised when a non-admin user tries to access an admin-only resource."""
    pass