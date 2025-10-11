"""
Defines the API endpoints for managing and viewing book categories.
"""
from flask import Blueprint, jsonify, request
from app.services import category_service
from app.schemas.category_schemas import CategoryPublic, CategoryCreate, CategoryUpdate
from app.core.security import admin_required

category_bp = Blueprint('categories', __name__)

# --- Public Route ---
@category_bp.route('/api/categories', methods=['GET'])
def handle_get_categories():
    """Retrieves a list of all public categories."""
    categories = category_service.get_all_categories()
    categories_data = [CategoryPublic.model_validate(cat).model_dump() for cat in categories]
    return jsonify(categories_data)

# --- Admin Routes ---
@category_bp.route('/api/admin/categories', methods=['POST'])
@admin_required
def handle_create_category():
    """Handles the creation of a new category."""
    data = request.get_json()
    category_data = CategoryCreate(**data)
    new_category = category_service.create_category(category_data)
    return jsonify(CategoryPublic.model_validate(new_category).model_dump()), 201

@category_bp.route('/api/admin/categories/<int:category_id>', methods=['PUT'])
@admin_required
def handle_update_category(category_id):
    """Handles updating an existing category."""
    data = request.get_json()
    category_data = CategoryUpdate(**data)
    updated_category = category_service.update_category(category_id, category_data)
    if not updated_category:
        return jsonify({"error": "Category not found"}), 404
    return jsonify(CategoryPublic.model_validate(updated_category).model_dump()), 200

@category_bp.route('/api/admin/categories/<int:category_id>', methods=['DELETE'])
@admin_required
def handle_delete_category(category_id):
    """Handles soft-deleting a category."""
    deleted_category = category_service.delete_category(category_id)
    if not deleted_category:
        return jsonify({"error": "Category not found"}), 404
    return jsonify({"message": f"Category '{deleted_category.name}' has been deleted."}), 200