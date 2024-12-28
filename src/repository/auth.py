from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from ...lib.models import User
from ...lib.schemas import UserSchema, UserPublic
from typing import Optional
from os import getenv

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

# Configuration for JWT
SECRET_KEY = getenv('OUTSTAGRAM_SECRET_KEY', '')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Initialize Argon2 hasher
ph = PasswordHasher()

# Function to hash a password
def get_password_hash(password: str) -> str:
    return ph.hash(password)

# Function to verify a password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def authorize(token: str, db: Session) -> UserPublic:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception

    return UserPublic(
        user_id=user.user_id,
        fullname=user.fullname,
        username=user.username,
        bio=user.bio,
        highlighted_posts=user.highlighted_posts,
        authored_posts=user.authored_posts
    )
    return


# Function to create a new user
def create_user(db: Session, user: User) -> UserPublic:
    # Check if the username already exists
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise ValueError("Username already registered")

    hashed = get_password_hash(user.password)

    
    new_user = User(
        fullname=user.fullname,
        username=user.username,
        email=user.email,
        password=hashed,
        bio=user.bio,
        date_of_birth=user.date_of_birth,
    )
    
    # Add the new user to the session and commit to the database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # Refresh the instance to get the latest data
    
    return UserPublic(
        #user_id=new_user.user_id,
        fullname=new_user.fullname,
        username=new_user.username,
        bio=new_user.bio,
    )

# Function to create an access token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Function to authenticate a user
def authenticate_user(db: Session, username: str, password: str) -> Optional[UserPublic]:
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return None  # Return None if authentication fails
    return UserPublic(
        user_id=user.user_id,
        fullname=user.fullname,
        username=user.username,
        bio=user.bio,
        highlighted_posts=user.highlighted_posts,
        authored_posts=user.authored_posts
    )

