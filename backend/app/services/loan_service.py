import datetime
from app.models import Loan, BookCopy, User, Book
from app.core.exceptions import ConcurrencyException, BookNotAvailableException
from app.tasks import send_loan_confirmation_email
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import joinedload
from app.schemas.loan_schemas import LoanCreate

from app.repositories.book_copy_repository import BookCopyRepository
from app.repositories.loan_repository import LoanRepository 

book_copy_repo = BookCopyRepository()
loan_repo = LoanRepository()

def _lock_and_create_loan(user: User, book_copy_id: int, loan_days: int):
    # Private helper function containing the core pessimistic locking logic.
    
    try:
        book_copy = book_copy_repo.get_and_lock(book_copy_id) 

        if not book_copy:
            raise BookNotAvailableException("This book copy does not exist.")
        
        if book_copy.status != 'available':
            raise BookNotAvailableException("This book copy is not available for loan.")

        book_copy.status = 'loaned'
        
        due_date = datetime.datetime.utcnow() + datetime.timedelta(days=loan_days)
        new_loan = Loan(user_id=user.id, book_copy_id=book_copy_id, due_date=due_date)

        loan_repo.add(new_loan)
        loan_repo.commit() 

        send_loan_confirmation_email.delay(new_loan.id)
        
        return new_loan

    except OperationalError:
        loan_repo.rollback()
        raise ConcurrencyException("This book copy is currently being processed. Please try again in a moment.")
    
    except Exception as e:
        loan_repo.rollback()
        raise e

def create_loan(user: User, loan_data: LoanCreate):

    # Main service function. Finds an available copy for the given book_id and loans it.

    available_copy = book_copy_repo.find_available_for_book(loan_data.book_id)

    if not available_copy:
        raise BookNotAvailableException("No available copies of this book were found.")
    
    # Call our locking helper with the found copy_id
    return _lock_and_create_loan(user, available_copy.id, loan_data.loan_days)

def get_user_loans(user_id: int):
    # Fetches all loans for a specific user.
    return loan_repo.find_by_user_id_with_details(user_id)