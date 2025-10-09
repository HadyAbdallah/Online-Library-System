from flask import Blueprint, request, jsonify
from app.services import book_service
from app.schemas.book_schemas import BookPublic

book_bp = Blueprint('books', __name__, url_prefix='/api/books')

@book_bp.route('/', methods=['GET'])
def list_books():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search_query = request.args.get('q', type=str)
    category_name = request.args.get('category', type=str)

    books, total_pages, total_items = book_service.get_all_books(
        page=page,
        per_page=per_page,
        search_query=search_query,
        category_name=category_name
    )

    # Use the Pydantic model to serialize the data
    books_data = [BookPublic.model_validate(book).model_dump() for book in books]

    return jsonify({
        "books": books_data,
        "page": page,
        "total_pages": total_pages,
        "total_items": total_items
    })

@book_bp.route('/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = book_service.get_book_by_id(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    return jsonify(BookPublic.model_validate(book).model_dump())