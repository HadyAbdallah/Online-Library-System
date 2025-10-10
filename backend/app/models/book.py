from app.extensions import db

# Many-to-Many join table for books and categories
book_category_link = db.Table('book_category_link',
    db.Column('book_id', db.Integer, db.ForeignKey('books.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('categories.id'), primary_key=True)
)

class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    author = db.Column(db.String(150), nullable=False, index=True)
    isbn = db.Column(db.String(13), unique=True, nullable=False)
    publication_year = db.Column(db.Integer)
    image_url = db.Column(db.String(255), nullable=True)
    deleted_at = db.Column(db.DateTime, nullable=True, index=True)

    # Many-to-Many relationship to Category
    categories = db.relationship('Category', secondary=book_category_link, lazy='subquery',
                                 backref=db.backref('books', lazy=True))

    # One-to-Many relationship to BookCopy
    copies = db.relationship(
        'BookCopy',
        primaryjoin="and_(Book.id==BookCopy.book_id, BookCopy.deleted_at==None)",
        backref='book',
        lazy='select'
    )

class BookCopy(db.Model):
    __tablename__ = 'book_copies'
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False, default='available', index=True) # 'available', 'loaned', 'maintenance'
    deleted_at = db.Column(db.DateTime, nullable=True, index=True)

    # This version column is the key to our optimistic locking strategy later
    version = db.Column(db.Integer, nullable=False, default=1)