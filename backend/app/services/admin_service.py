"""
Contains administrative logic for managing the book catalog.
"""
from app.models import Book, BookCopy, Category
from app.schemas.admin_schemas import BookCreate, BookUpdate
from app.core.redis_client import redis_client
from sqlalchemy.exc import IntegrityError
import datetime
from app.core import file_handler

from app.repositories.book_repository import BookRepository
from app.repositories.book_copy_repository import BookCopyRepository
from app.repositories.category_repository import CategoryRepository

book_repo = BookRepository()
book_copy_repo = BookCopyRepository()
category_repo = CategoryRepository()

def create_book(book_data: BookCreate, image_file=None):
    """Creates a new book."""
    new_book = Book(
        title=book_data.title,
        author=book_data.author,
        isbn=book_data.isbn,
        publication_year=book_data.publication_year,
        description=book_data.description
    )
    if book_data.category_ids:
        categories = category_repo.get_by_ids(book_data.category_ids)
        new_book.categories.extend(categories)

    book_repo.add(new_book)
    try:
        book_repo.commit()
    except IntegrityError:
        book_repo.rollback()
        raise ValueError(f"A book with ISBN {book_data.isbn} already exists.")

    if image_file:
        image_url = file_handler.save_book_image(image_file)
        new_book.image_url = image_url
        book_repo.commit()

    return new_book

def update_book(book_id: int, book_data: BookUpdate, image_file=None):
    """Updates a book's details and invalidates its cache."""
    book = book_repo.get_by_id(book_id)
    if not book:
        return None

    for key, value in book_data.model_dump(exclude_unset=True).items():
        if key == "category_ids":
            categories = category_repo.get_by_ids(value)
            book.categories = categories
        else:
            setattr(book, key, value)

    if image_file:
        image_url = file_handler.save_book_image(image_file)
        book.image_url = image_url

    try:
        book_repo.commit()
    except IntegrityError:
        book_repo.rollback()
        raise ValueError(f"A book with the provided ISBN already exists.")

    # Must remove the old data from cache to avoid serving stale information.
    cache_key = f"book:{book_id}"
    redis_client.delete(cache_key)

    return book

def delete_book(book_id: int):
    """Soft deletes a book, its copies, and invalidates the cache."""
    book = book_repo.get_by_id(book_id)
    if not book:
        return None

    book.deleted_at = datetime.datetime.utcnow()
    book_copy_repo.soft_delete_by_book_id(book_id)
    book_repo.commit()

    # Invalidate cache for the deleted book.
    cache_key = f"book:{book_id}"
    redis_client.delete(cache_key)

    return book

def add_book_copy(book_id: int):
    """Adds a new copy for an existing book."""
    book = book_repo.get_by_id(book_id)
    if not book:
        return None

    new_copy = BookCopy(book_id=book.id)
    book_copy_repo.add(new_copy)
    book_copy_repo.commit()
    return new_copy

def delete_book_copy(copy_id: int):
    """Soft deletes a book copy and invalidates the parent book's cache."""
    copy = book_copy_repo.get_by_id(copy_id)
    if not copy or copy.deleted_at is not None:
        return None

    copy.deleted_at = datetime.datetime.utcnow()
    book_copy_repo.commit()

    # The book's available copy count has changed, so its cache is now invalid.
    cache_key = f"book:{copy.book_id}"
    redis_client.delete(cache_key)

    return copy