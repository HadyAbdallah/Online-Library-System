from flask import Blueprint, request, jsonify
from pydantic import ValidationError
import datetime
import jwt

from app.schemas.auth_schemas import UserCreate, UserLogin
from app.services import auth_service
from app.config import settings

# A Blueprint is a way to organize a group of related routes
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        user_data = UserCreate(**request.json)
        auth_service.register_user(user_data)
        return jsonify({"message": "User registered successfully"}), 201
    except ValidationError as e:
        return jsonify(e.errors()), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 409 # 409 Conflict

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        login_data = UserLogin(**request.json)
        user = auth_service.authenticate_user(login_data.email, login_data.password)

        if not user:
            return jsonify({"error": "Invalid credentials"}), 401

        # Create the JWT
        token_payload = {
            'sub': user.id, # 'sub' is standard for subject/user_id
            'role': user.role,
            'iat': datetime.datetime.utcnow(), # Issued at
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24) # Expiration time
        }
        access_token = jwt.encode(token_payload, settings.SECRET_KEY, algorithm='HS256')

        return jsonify({"access_token": access_token, "token_type": "bearer"})

    except ValidationError as e:
        return jsonify(e.errors()), 400