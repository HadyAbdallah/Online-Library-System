import json
from app.models import Book, Category
from app.core.redis_client import redis_client
from app.schemas.book_schemas import BookPublic

def get_all_books(page: int, per_page: int, search_query: str | None, category_name: str | None):
    # 1. Create a unique cache key based on all the function's arguments
    cache_key = f"books:page={page}:per_page={per_page}:q={search_query}:cat={category_name}"

    # 2. Try to get the data from Redis
    cached_books = redis_client.get(cache_key)

    if cached_books:
        # 3. If found (cache hit), decode the JSON and return it
        return json.loads(cached_books)

    # 4. If not found (cache miss), query the database as before
    query = Book.query
    if category_name:
        query = query.join(Book.categories).filter(Category.name == category_name)
    if search_query:
        search_filter = f"%{search_query}%"
        query = query.filter((Book.title.ilike(search_filter)) | (Book.author.ilike(search_filter)))

    paginated_books = query.paginate(page=page, per_page=per_page, error_out=False)
    books = paginated_books.items

    # Prepare the data for caching and for the response
    books_data = [BookPublic.model_validate(book).model_dump() for book in books]
    response_data = {
        "books": books_data,
        "page": page,
        "total_pages": paginated_books.pages,
        "total_items": paginated_books.total
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
    book = Book.query.get(book_id)
    if not book:
        return None

    book_data = BookPublic.model_validate(book).model_dump()

    # 5. Store the result in Redis with a 5-minute expiration
    redis_client.set(cache_key, json.dumps(book_data), ex=300)

    return book_data