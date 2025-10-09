from flask import Flask
from .config import settings
from .extensions import db, migrate, bcrypt

# blueprint
from .api.auth_routes import auth_bp
from .api.book_routes import book_bp

from . import models

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config['SECRET_KEY'] = settings.SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = settings.DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)

    # Register the blueprint with the app
    app.register_blueprint(auth_bp)
    app.register_blueprint(book_bp)

    return app