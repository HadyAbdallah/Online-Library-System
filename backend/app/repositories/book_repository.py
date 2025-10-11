from .base_repository import BaseRepository
from app.models import Book, Category
from app.extensions import db

class BookRepository(BaseRepository):
    def __init__(self):
        super().__init__(Book)

    def get_active_by_id(self, book_id: int):
            # This method finds a book only if it has not been soft-deleted.
        return db.session.query(self.model).filter(
            self.model.id == book_id,
            self.model.deleted_at.is_(None)
        ).first()

    def search_and_filter(self, page, per_page, search_query, category_name):
        query = db.session.query(self.model).filter(self.model.deleted_at.is_(None))

        if category_name:
            query = query.join(Book.categories).filter(Category.name == category_name)

        if search_query:
            search_filter = f"%{search_query}%"
            query = query.filter(
                (Book.title.ilike(search_filter)) | (Book.author.ilike(search_filter))
            )

        paginated_books = query.paginate(page=page, per_page=per_page, error_out=False)
        return paginated_books.items, paginated_books.pages, paginated_books.total