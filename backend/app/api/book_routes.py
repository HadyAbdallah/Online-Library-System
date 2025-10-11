"""
Defines the public API endpoints for browsing and viewing books.
"""
from flask import Blueprint, request, jsonify
from app.services import book_service

book_bp = Blueprint('books', __name__, url_prefix='/api/books')

@book_bp.route('/', methods=['GET'])
def list_books():
    """Retrieves a paginated and filterable list of books."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search_query = request.args.get('q', type=str)
    category_name = request.args.get('category', type=str)

    # The service layer handles caching and returns the final dictionary.
    response_data = book_service.get_all_books(
        page=page, per_page=per_page, search_query=search_query, category_name=category_name
    )
    return jsonify(response_data)

@book_bp.route('/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """Retrieves details for a single book by its ID."""
    # The service layer handles caching and returns the final dictionary.
    book = book_service.get_book_by_id(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    return jsonify(book)