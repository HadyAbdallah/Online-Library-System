from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from app.core.security import admin_required
from app.services import admin_service ,loan_service
from app.schemas.admin_schemas import BookCreate, BookUpdate
from app.schemas.book_schemas import BookPublic  
from app.schemas.loan_schemas import AdminLoanView

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


@admin_bp.route('/books', methods=['POST'])
@admin_required
def handle_create_book():

    book_data = BookCreate(**request.form.to_dict())
    image_file = request.files.get('image')
    new_book = admin_service.create_book(book_data, image_file)
    return jsonify(BookPublic.model_validate(new_book).model_dump()), 201


@admin_bp.route('/books/<int:book_id>', methods=['PUT'])
@admin_required
def handle_update_book(book_id):

    book_data = BookUpdate(**request.form.to_dict())
    image_file = request.files.get('image')

    updated_book = admin_service.update_book(book_id, book_data, image_file)
    if not updated_book:
        return jsonify({"error": "Book not found"}), 404
    return jsonify(BookPublic.model_validate(updated_book).model_dump()), 200


@admin_bp.route('/books/<int:book_id>', methods=['DELETE'])
@admin_required
def handle_delete_book(book_id):
    deleted_book = admin_service.delete_book(book_id)
    if not deleted_book:
        return jsonify({"error": "Book not found"}), 404

    return jsonify({"message": f"Book '{deleted_book.title}' has been deleted."}), 200


@admin_bp.route('/books/<int:book_id>/copies', methods=['POST'])
@admin_required
def handle_add_book_copy(book_id):
    new_copy = admin_service.add_book_copy(book_id)
    if not new_copy:
        return jsonify({"error": "Book not found"}), 404
    return jsonify({"message": "Book copy added successfully", "copy_id": new_copy.id}), 201


@admin_bp.route('/copies/<int:copy_id>', methods=['DELETE'])
@admin_required
def handle_delete_book_copy(copy_id):
    deleted_copy = admin_service.delete_book_copy(copy_id)
    if not deleted_copy:
        return jsonify({"error": "Book copy not found"}), 404

    return jsonify({"message": f"Book copy ID {copy_id} has been deleted."}), 200

@admin_bp.route('/loans', methods=['GET'])
@admin_required
def handle_get_active_loans():
    active_loans = loan_service.get_all_active_loans()
    loans_data = [AdminLoanView.model_validate(loan).model_dump() for loan in active_loans]
    return jsonify(loans_data)
