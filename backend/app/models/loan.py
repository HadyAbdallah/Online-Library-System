from app.extensions import db
import datetime

class Loan(db.Model):
    __tablename__ = 'loans'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    book_copy_id = db.Column(db.Integer, db.ForeignKey('book_copies.id'), nullable=False, index=True)
    loan_date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=False)
    return_date = db.Column(db.DateTime, nullable=True)

    user = db.relationship('User', backref=db.backref('loans', lazy=True))
    book_copy = db.relationship('BookCopy', backref=db.backref('loans', lazy=True))