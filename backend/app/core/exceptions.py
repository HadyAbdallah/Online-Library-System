class ConcurrencyException(Exception):
    """Raised when an optimistic locking conflict occurs."""
    pass

class BookNotAvailableException(Exception):
    """Raised when a book copy is not available for loan."""
    pass