"""
Defines the API endpoints for user authentication: register, login, and logout.
"""
from flask import Blueprint, request, jsonify, g
import datetime
import jwt
import uuid
from app.core.security import jwt_required
from app.core.redis_client import redis_client
from app.schemas.auth_schemas import UserCreate, UserLogin
from app.services import auth_service
from app.config import settings

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    """Handles new user registration."""
    user_data = UserCreate(**request.json)
    auth_service.register_user(user_data)
    return jsonify({"message": "User registered successfully"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """Handles user login and JWT token generation."""
    login_data = UserLogin(**request.json)
    user = auth_service.authenticate_user(login_data.email, login_data.password)

    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    # Create the JWT payload.
    token_payload = {
        'sub': user.id,  # Standard claim for subject (user ID)
        'role': user.role,
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24),
        'jti': str(uuid.uuid4()) # Unique token ID for denylisting
    }
    access_token = jwt.encode(token_payload, settings.SECRET_KEY, algorithm='HS256')

    return jsonify({"access_token": access_token, "token_type": "bearer"})

@auth_bp.route('/logout', methods=['POST'])
@jwt_required
def logout():
    """Handles user logout by adding the token to a denylist."""
    # The token payload is attached to the global `g` object by our decorator.
    payload = g.jwt_payload
    jti = payload['jti']
    exp = payload['exp']

    # Add the token's unique ID (jti) to the Redis denylist until it expires.
    time_to_expire = datetime.datetime.fromtimestamp(exp) - datetime.datetime.utcnow()
    redis_client.set(f"denylist:{jti}", "true", ex=time_to_expire)

    return jsonify({"message": "Successfully logged out."}), 200