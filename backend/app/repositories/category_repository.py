from .base_repository import BaseRepository
from app.models import Category
from app.extensions import db

class CategoryRepository(BaseRepository):
    def __init__(self):
        super().__init__(Category)

    def get_by_ids(self, category_ids: list):
        return db.session.query(self.model).filter(self.model.id.in_(category_ids)).all()