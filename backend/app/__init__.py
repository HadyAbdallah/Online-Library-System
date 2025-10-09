from flask import Flask
from .config import settings
from .extensions import db, migrate, bcrypt

# blueprint
from .api.auth_routes import auth_bp

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = settings.SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = settings.DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)

    # Register the blueprint with the app
    app.register_blueprint(auth_bp)

    return app