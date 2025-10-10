from app.extensions import db
from app.models import Book, BookCopy, Category
from app.schemas.admin_schemas import BookCreate, BookUpdate
from app.core.redis_client import redis_client
from sqlalchemy.exc import IntegrityError
import datetime

def create_book(book_data: BookCreate):
    new_book = Book(
        title=book_data.title,
        author=book_data.author,
        isbn=book_data.isbn,
        publication_year=book_data.publication_year,
        description=book_data.description,
        image_url=book_data.image_url
    )
    if book_data.category_ids:
        categories = Category.query.filter(Category.id.in_(book_data.category_ids)).all()
        new_book.categories.extend(categories)

    db.session.add(new_book)

    try:
        db.session.commit()
    except IntegrityError:
        # Important: roll back the session to a clean state
        db.session.rollback()
        # Raise a more specific, user-friendly error
        raise ValueError(f"A book with ISBN {book_data.isbn} already exists.")


    return new_book

def update_book(book_id: int, book_data: BookUpdate):
    book = Book.query.get(book_id)
    if not book:
        return None

    # Update fields from the Pydantic model
    for key, value in book_data.model_dump(exclude_unset=True).items():
        if key == "category_ids":
            categories = Category.query.filter(Category.id.in_(value)).all()
            book.categories = categories
        else:
            setattr(book, key, value)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ValueError(f"A book with the provided ISBN already exists.")

    # --- Cache Invalidation ---
    # When a book is updated, its old data in the cache is now stale.
    # We must delete it.
    cache_key = f"book:{book_id}"
    redis_client.delete(cache_key)

    return book

def delete_book(book_id: int):
    book = Book.query.get(book_id)
    if not book:
        return None

    now = datetime.datetime.utcnow()

    # Soft delete the main book record
    book.deleted_at = now

    # Find all active copies of this book and soft delete them too
    BookCopy.query.filter(
        BookCopy.book_id == book_id,
        BookCopy.deleted_at.is_(None)
    ).update({'deleted_at': now})

    db.session.commit()

    # Invalidate the cache for this specific book
    cache_key = f"book:{book_id}"
    redis_client.delete(cache_key)

    return book

def add_book_copy(book_id: int):
    book = Book.query.get(book_id)
    if not book:
        return None

    new_copy = BookCopy(book_id=book.id)
    db.session.add(new_copy)
    db.session.commit()
    return new_copy

def delete_book_copy(copy_id: int):
    copy = BookCopy.query.get(copy_id)
    if not copy or copy.deleted_at is not None:
        return None

    copy.deleted_at = datetime.datetime.utcnow()
    db.session.commit()

    # When a copy's status changes, the main book's detail
    # cache is now out of date. We should invalidate it.
    cache_key = f"book:{copy.book_id}"
    redis_client.delete(cache_key)

    return copy