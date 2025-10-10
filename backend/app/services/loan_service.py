import datetime
from app.extensions import db
from app.models import Loan, BookCopy, User
from app.core.exceptions import ConcurrencyException, BookNotAvailableException

def create_loan(user: User, book_copy_id: int):
    book_copy = BookCopy.query.get(book_copy_id)

    if not book_copy or book_copy.status != 'available':
        raise BookNotAvailableException("This book copy is not available for loan.")

    try:
        # This is the core of optimistic locking.
        # We try to update the book copy's status and increment its version
        # but only if the status is still 'available'.
        # The database ensures this is an atomic operation.
        rows_updated = db.session.query(BookCopy).filter(
            BookCopy.id == book_copy_id,
            BookCopy.status == 'available'
        ).update({
            'status': 'loaned',
            'version': BookCopy.version + 1
        })

        # If no rows were updated, it means another transaction changed the
        # copy's status between our initial check and our update attempt.
        if rows_updated == 0:
            db.session.rollback()
            raise ConcurrencyException("This book was just borrowed by someone else. Please try another copy.")

        # If the update succeeded, we can create the loan record.
        due_date = datetime.datetime.utcnow() + datetime.timedelta(weeks=2)
        new_loan = Loan(user_id=user.id, book_copy_id=book_copy_id, due_date=due_date)

        db.session.add(new_loan)
        db.session.commit()
        return new_loan

    except Exception as e:
        db.session.rollback()
        # Re-raise the exception to be handled by the route
        raise e