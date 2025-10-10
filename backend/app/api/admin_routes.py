from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from app.core.security import admin_required
from app.services import admin_service
from app.schemas.admin_schemas import BookCreate, BookUpdate
from app.schemas.book_schemas import BookPublic # For response serialization

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@admin_bp.route('/books', methods=['POST'])
@admin_required
def handle_create_book():
    try:
        book_data = BookCreate(**request.json)
        new_book = admin_service.create_book(book_data)
        return jsonify(BookPublic.model_validate(new_book).model_dump()), 201
    except ValidationError as e:
        return jsonify(e.errors()), 400
    except ValueError as e: 
        return jsonify({"error": str(e)}), 409

@admin_bp.route('/books/<int:book_id>', methods=['PUT'])
@admin_required
def handle_update_book(book_id):
    try:
        book_data = BookUpdate(**request.json)
        updated_book = admin_service.update_book(book_id, book_data)
        if not updated_book:
            return jsonify({"error": "Book not found"}), 404
        return jsonify(BookPublic.model_validate(updated_book).model_dump()), 200
    except ValidationError as e:
        return jsonify(e.errors()), 400

@admin_bp.route('/books/<int:book_id>/copies', methods=['POST'])
@admin_required
def handle_add_book_copy(book_id):
    new_copy = admin_service.add_book_copy(book_id)
    if not new_copy:
        return jsonify({"error": "Book not found"}), 404
    return jsonify({"message": "Book copy added successfully", "copy_id": new_copy.id}), 201