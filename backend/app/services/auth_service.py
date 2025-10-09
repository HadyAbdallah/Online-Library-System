from app.extensions import db, bcrypt
from app.models.user import User
from app.schemas.auth_schemas import UserCreate

def register_user(user_data: UserCreate):
    # Check if user already exists
    if User.query.filter((User.username == user_data.username) | (User.email == user_data.email)).first():
        raise ValueError("Username or email already exists.")

    hashed_password = bcrypt.generate_password_hash(user_data.password).decode('utf-8')
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_password
    )
    db.session.add(new_user)
    db.session.commit()
    return new_user

def authenticate_user(email: str, password: str) -> User | None:
    user = User.query.filter_by(email=email).first()
    if user and bcrypt.check_password_hash(user.password_hash, password):
        return user
    return None