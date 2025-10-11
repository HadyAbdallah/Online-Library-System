from .base_repository import BaseRepository
from app.models import BookCopy
from app.extensions import db
import datetime

class BookCopyRepository(BaseRepository):
    def __init__(self):
        super().__init__(BookCopy)

    def find_available_for_book(self, book_id):
        return db.session.query(self.model).filter_by(
            book_id=book_id,
            status='available',
            deleted_at=None
        ).first()

    def get_and_lock(self, copy_id):
        return db.session.query(self.model).filter(
            self.model.id == copy_id
        ).with_for_update(nowait=True).first()

    def soft_delete_by_book_id(self, book_id):
        self.model.query.filter(
            self.model.book_id == book_id,
            self.model.deleted_at.is_(None)
        ).update({'deleted_at': datetime.datetime.utcnow()})