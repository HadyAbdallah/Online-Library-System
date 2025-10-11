"""
Handles business logic for managing book categories.
"""
import datetime
from sqlalchemy.exc import IntegrityError
from app.repositories.category_repository import CategoryRepository
from app.schemas.category_schemas import CategoryCreate, CategoryUpdate
from app.models import Category

category_repo = CategoryRepository()

def get_all_categories():
    """Retrieves all active categories."""
    return category_repo.get_all_active()

def create_category(category_data: CategoryCreate):
    """Creates a new category."""
    new_category = Category(
        name=category_data.name,
        description=category_data.description
    )
    category_repo.add(new_category)
    try:
        category_repo.commit()
    except IntegrityError:
        category_repo.rollback()
        raise ValueError(f"A category with the name '{category_data.name}' already exists.")
    return new_category

def update_category(category_id: int, category_data: CategoryUpdate):
    """Updates an existing category."""
    category = category_repo.get_by_id(category_id)
    if not category or category.deleted_at:
        return None

    for key, value in category_data.model_dump(exclude_unset=True).items():
        setattr(category, key, value)

    try:
        category_repo.commit()
    except IntegrityError:
        category_repo.rollback()
        raise ValueError(f"A category with the name '{category_data.name}' already exists.")
    return category

def delete_category(category_id: int):
    """Soft deletes a category."""
    category = category_repo.get_by_id(category_id)
    if not category or category.deleted_at:
        return None

    category.deleted_at = datetime.datetime.utcnow()
    category_repo.commit()
    return category