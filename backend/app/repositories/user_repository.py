from .base_repository import BaseRepository
from app.models import User
from app.extensions import db

class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__(User)

    def find_by_username_or_email(self, username: str, email: str):
        return db.session.query(self.model).filter(
            (self.model.username == username) | (self.model.email == email)
        ).first()

    def find_by_email(self, email: str):
        return db.session.query(self.model).filter_by(email=email).first()