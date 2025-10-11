from .base_repository import BaseRepository
from app.models import Loan, BookCopy
from app.extensions import db
from sqlalchemy.orm import joinedload

class LoanRepository(BaseRepository):
    def __init__(self):
        super().__init__(Loan)

    def find_by_user_id_with_details(self, user_id: int):
        return db.session.query(self.model).options(
            joinedload(self.model.book_copy).joinedload(BookCopy.book)
        ).filter(self.model.user_id == user_id).order_by(self.model.loan_date.desc()).all()

    def find_all_active_with_details(self): # <-- ADD THIS NEW METHOD
        return db.session.query(self.model).options(
            joinedload(self.model.user),
            joinedload(self.model.book_copy).joinedload(BookCopy.book)
        ).filter(self.model.return_date.is_(None)).order_by(self.model.due_date.asc()).all()