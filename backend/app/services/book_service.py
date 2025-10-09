from app.models.book import Book
from app.models.category import  Category

def get_all_books(page: int, per_page: int, search_query: str | None, category_name: str | None):
    query = Book.query

    # Filtering
    if category_name:
        query = query.join(Book.categories).filter(Category.name == category_name)

    # Searching
    if search_query:
        # .ilike() provides case-insensitive matching.
        # This is a simple search. For a large-scale app, a dedicated
        # search engine or PostgreSQL's full-text search would be better.
        search_filter = f"%{search_query}%"
        query = query.filter(
            (Book.title.ilike(search_filter)) | (Book.author.ilike(search_filter))
        )

    # Pagination
    paginated_books = query.paginate(page=page, per_page=per_page, error_out=False)
    return paginated_books.items, paginated_books.pages, paginated_books.total

def get_book_by_id(book_id: int):
    return Book.query.get(book_id)