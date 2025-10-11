from app.models import Book, BookCopy, Category
from app.schemas.admin_schemas import BookCreate, BookUpdate
from app.core.redis_client import redis_client
from sqlalchemy.exc import IntegrityError
import datetime
from app.core import file_handler 

# Import repositories
from app.repositories.book_repository import BookRepository
from app.repositories.book_copy_repository import BookCopyRepository
from app.repositories.category_repository import CategoryRepository

# Instantiate them
book_repo = BookRepository()
book_copy_repo = BookCopyRepository()
category_repo = CategoryRepository()

def create_book(book_data: BookCreate, image_file=None):
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

    # --- Cache Invalidation ---
    # When a book is updated, its old data in the cache is now stale.
    # We must delete it.
    cache_key = f"book:{book_id}"
    redis_client.delete(cache_key)

    return book

def delete_book(book_id: int):
    book = book_repo.get_by_id(book_id)
    if not book:
        return None

    # Soft delete the main book record
    book.deleted_at = datetime.datetime.utcnow()

    # Find all active copies of this book and soft delete them too
    book_copy_repo.soft_delete_by_book_id(book_id)
    
    book_repo.commit()

    # Invalidate the cache for this specific book
    cache_key = f"book:{book_id}"
    redis_client.delete(cache_key)

    return book

def add_book_copy(book_id: int):
    book = book_repo.get_by_id(book_id)
    if not book:
        return None

    new_copy = BookCopy(book_id=book.id)
    book_copy_repo.add(new_copy)
    book_copy_repo.commit()
    return new_copy

def delete_book_copy(copy_id: int):
    copy = book_copy_repo.get_by_id(copy_id)
    if not copy or copy.deleted_at is not None:
        return None

    copy.deleted_at = datetime.datetime.utcnow()
    book_copy_repo.commit()

    # When a copy's status changes, the main book's detail
    # cache is now out of date. We should invalidate it.
    cache_key = f"book:{copy.book_id}"
    redis_client.delete(cache_key)

    return copy