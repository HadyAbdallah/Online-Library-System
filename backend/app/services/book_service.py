import json
from app.core.redis_client import redis_client
from app.schemas.book_schemas import BookPublic
from app.repositories.book_repository import BookRepository

# Instantiate the repository
book_repo = BookRepository()

def get_all_books(page: int, per_page: int, search_query: str | None, category_name: str | None):
    # 1. Create a unique cache key based on all the function's arguments
    cache_key = f"books:page={page}:per_page={per_page}:q={search_query}:cat={category_name}"

    # 2. Try to get the data from Redis
    cached_books = redis_client.get(cache_key)

    if cached_books:
        # 3. If found (cache hit), decode the JSON and return it
        return json.loads(cached_books)

    # 4. If not found in cache, call the repository to get data from the DB
    books, total_pages, total_items = book_repo.search_and_filter(
        page, per_page, search_query, category_name
    )

    # Prepare the data for caching and for the response
    books_data = [BookPublic.model_validate(book).model_dump() for book in books]
    response_data = {
        "books": books_data,
        "page": page,
        "total_pages": total_pages,
        "total_items": total_items
    }

    # 5. Store the result in Redis with a 5-minute expiration time (300 seconds)
    redis_client.set(cache_key, json.dumps(response_data), ex=300)

    return response_data


def get_book_by_id(book_id: int):
    # 1. Create a unique cache key for this specific book
    cache_key = f"book:{book_id}"

    # 2. Try to get the data from Redis
    cached_book = redis_client.get(cache_key)

    if cached_book:
        # 3. If found (cache hit), decode and return it
        return json.loads(cached_book)

    # 4. If not found (cache miss), query the database
    book = book_repo.get_active_by_id(book_id)
    
    if not book:
        return None

    book_data = BookPublic.model_validate(book).model_dump()

    # 5. Store the result in Redis with a 5-minute expiration
    redis_client.set(cache_key, json.dumps(book_data), ex=300)

    return book_data