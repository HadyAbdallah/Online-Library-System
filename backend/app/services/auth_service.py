"""
Handles user registration and authentication logic.
"""
from app.extensions import bcrypt
from app.models.user import User
from app.schemas.auth_schemas import UserCreate
from app.repositories.user_repository import UserRepository

user_repo = UserRepository()

def register_user(user_data: UserCreate):
    """Registers a new user."""
    existing_user = user_repo.find_by_username_or_email(user_data.username, user_data.email)
    if existing_user:
        raise ValueError("Username or email already exists.")

    hashed_password = bcrypt.generate_password_hash(user_data.password).decode('utf-8')
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_password
    )
    user_repo.add(new_user)
    user_repo.commit()
    return new_user

def authenticate_user(email: str, password: str) -> User | None:
    """Authenticates a user by email and password."""
    user = user_repo.find_by_email(email)

    if user and bcrypt.check_password_hash(user.password_hash, password):
        return user
    return None