from flask import Blueprint, request, jsonify
from pydantic import ValidationError
import datetime
import jwt
import uuid
from flask import g
from app.core.security import jwt_required
from app.core.redis_client import redis_client

from app.schemas.auth_schemas import UserCreate, UserLogin
from app.services import auth_service
from app.config import settings

# A Blueprint is a way to organize a group of related routes
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
def register():

    user_data = UserCreate(**request.json)
    auth_service.register_user(user_data)
    return jsonify({"message": "User registered successfully"}), 201


@auth_bp.route('/login', methods=['POST'])
def login():

    login_data = UserLogin(**request.json)
    user = auth_service.authenticate_user(
        login_data.email, login_data.password)

    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    # Create the JWT
    token_payload = {
        'sub': user.id,  # 'sub' is standard for subject/user_id
        'role': user.role,
        'iat': datetime.datetime.utcnow(),  # Issued at
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24),  # Expiration time
        'jti': str(uuid.uuid4())
    }
    access_token = jwt.encode(
        token_payload, settings.SECRET_KEY, algorithm='HS256')

    return jsonify({"access_token": access_token, "token_type": "bearer"})


@auth_bp.route('/logout', methods=['POST'])
@jwt_required
def logout():
    # The payload is attached to g by our decorator 
    payload = g.jwt_payload
    jti = payload['jti']
    exp = payload['exp']
    
    # Calculate how long until the token expires and set the TTL in Redis
    time_to_expire = datetime.datetime.fromtimestamp(exp) - datetime.datetime.utcnow()
    
    # Add the token's JTI to the denylist
    redis_client.set(f"denylist:{jti}", "true", ex=time_to_expire)
    
    return jsonify({"message": "Successfully logged out."}), 200
