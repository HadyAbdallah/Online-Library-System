"""
Provides public logic for querying books, with a Redis caching layer.
"""
import json
from app.core.redis_client import redis_client
from app.schemas.book_schemas import BookPublic
from app.repositories.book_repository import BookRepository

book_repo = BookRepository()

def get_all_books(page: int, per_page: int, search_query: str | None, category_name: str | None):
    """Retrieves a paginated list of books, using a cache."""
    cache_key = f"books:page={page}:per_page={per_page}:q={search_query}:cat={category_name}"

    # Try to get the data from Redis.
    cached_books = redis_client.get(cache_key)

    if cached_books:
        return json.loads(cached_books)

    # If cache miss, query the database.
    books, total_pages, total_items = book_repo.search_and_filter(
        page, per_page, search_query, category_name
    )

    books_data = [BookPublic.model_validate(book).model_dump() for book in books]
    response_data = {
        "books": books_data,
        "page": page,
        "total_pages": total_pages,
        "total_items": total_items
    }

    # Store the result in Redis for 5 minutes.
    redis_client.set(cache_key, json.dumps(response_data), ex=300)

    return response_data


def get_book_by_id(book_id: int):
    """Retrieves a single book by ID, using a cache."""
    cache_key = f"book:{book_id}"

    # Try to get the data from Redis.
    cached_book = redis_client.get(cache_key)

    if cached_book:
        return json.loads(cached_book)

    # If cache miss, query the database.
    book = book_repo.get_active_by_id(book_id)

    if not book:
        return None

    book_data = BookPublic.model_validate(book).model_dump()

    # Store the result in Redis for 5 minutes.
    redis_client.set(cache_key, json.dumps(book_data), ex=300)

    return book_data