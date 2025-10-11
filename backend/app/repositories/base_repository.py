from app.extensions import db

class BaseRepository:
    def __init__(self, model):
        self.model = model

    def get_by_id(self, entity_id):
        return db.session.get(self.model, entity_id)

    def get_all(self):
        return db.session.query(self.model).all()

    def add(self, entity):
        db.session.add(entity)

    def commit(self):
        db.session.commit()

    def rollback(self):
        db.session.rollback()