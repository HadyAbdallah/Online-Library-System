import datetime
from app.extensions import db
from app.models import Loan, BookCopy, User, Book
from app.core.exceptions import ConcurrencyException, BookNotAvailableException
from app.tasks import send_loan_confirmation_email
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import joinedload
from app.schemas.loan_schemas import LoanCreate

def _lock_and_create_loan(user: User, book_copy_id: int, loan_days: int):
    # Private helper function containing the core pessimistic locking logic.
    
    try:
        book_copy = db.session.query(BookCopy).filter(
            BookCopy.id == book_copy_id
        ).with_for_update(nowait=True).first()

        if not book_copy:
            raise BookNotAvailableException("This book copy does not exist.")
        
        if book_copy.status != 'available':
            raise BookNotAvailableException("This book copy is not available for loan.")

        book_copy.status = 'loaned'
        
        due_date = datetime.datetime.utcnow() + datetime.timedelta(days=loan_days)
        new_loan = Loan(user_id=user.id, book_copy_id=book_copy_id, due_date=due_date)

        db.session.add(new_loan)
        db.session.commit()

        send_loan_confirmation_email.delay(new_loan.id)
        
        return new_loan

    except OperationalError:
        db.session.rollback()
        raise ConcurrencyException("This book copy is currently being processed. Please try again in a moment.")
    
    except Exception as e:
        db.session.rollback()
        raise e

def create_loan(user: User, loan_data: LoanCreate):

    # Main service function. Finds an available copy for the given book_id and loans it.

    available_copy = BookCopy.query.filter_by(
        book_id=loan_data.book_id,
        status='available',
        deleted_at=None
    ).first()

    if not available_copy:
        raise BookNotAvailableException("No available copies of this book were found.")
    
    # Call our locking helper with the found copy_id
    return _lock_and_create_loan(user, available_copy.id, loan_data.loan_days)

def get_user_loans(user_id: int):
    # Fetches all loans for a specific user.
    return Loan.query.options(
        joinedload(Loan.book_copy).joinedload(BookCopy.book)
    ).filter(Loan.user_id == user_id).order_by(Loan.loan_date.desc()).all()