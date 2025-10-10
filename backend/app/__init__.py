import os
from flask import Flask
from .config import settings
from .extensions import db, migrate, bcrypt

# blueprint
from .api.auth_routes import auth_bp
from .api.book_routes import book_bp
from .api.loan_routes import loan_bp
from .api.admin_routes import admin_bp

from . import models

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config['SECRET_KEY'] = settings.SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = settings.DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Ensure the instance and upload folders exist
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Construct the absolute path for the upload folder and ensure it exists
    upload_path = os.path.join(app.instance_path, settings.UPLOAD_FOLDER)
    os.makedirs(upload_path, exist_ok=True)
    
    # Store the absolute path in the app's config for later use
    app.config['UPLOAD_FOLDER'] = upload_path

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)

    # Register the blueprint with the app
    app.register_blueprint(auth_bp)
    app.register_blueprint(book_bp)
    app.register_blueprint(loan_bp)
    app.register_blueprint(admin_bp)

    return app