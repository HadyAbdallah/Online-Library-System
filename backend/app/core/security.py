"""
Implements security features like JWT handling and authorization decorators.
"""
from functools import wraps
from flask import request, g
import jwt
from app.config import settings
from app.models import User
from app.core.exceptions import (
    MissingTokenException, InvalidTokenException, ExpiredTokenException,
    AdminAccessRequiredException
)
from app.core.redis_client import redis_client

def _get_current_user_from_token():
    """
    Decodes the JWT from the Authorization header, validates it,
    and retrieves the corresponding user from the database.
    """
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        raise MissingTokenException('Authorization header is missing.')

    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        raise InvalidTokenException('Invalid token format. Expected "Bearer <token>".')

    token = parts[1]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        jti = payload.get('jti')

        # Check if the token has been revoked (logged out).
        if not jti or redis_client.get(f"denylist:{jti}"):
            raise InvalidTokenException('Token has been revoked.')

        user = User.query.get(payload['sub'])
        if user is None:
            raise InvalidTokenException('User not found.')

        # Attach the decoded payload to the global `g` object for potential use in the route.
        g.jwt_payload = payload

        return user, payload
    except jwt.ExpiredSignatureError:
        raise ExpiredTokenException('Token has expired.')
    except jwt.InvalidTokenError:
        raise InvalidTokenException('Invalid token.')

def jwt_required(f):
    """Decorator to protect routes that require a valid JWT token."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user, _ = _get_current_user_from_token()
        g.user = user # Attach user to the global `g` object for easy access in the route.
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to protect routes that require admin-level privileges."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user, payload = _get_current_user_from_token()
        if payload.get('role') != 'admin':
            raise AdminAccessRequiredException('Admin privileges required.')
        g.user = user
        return f(*args, **kwargs)
    return decorated_function