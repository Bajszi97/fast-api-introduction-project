from datetime import datetime, timedelta
import os
import bcrypt
import jwt
from repositories import UserRepository
from models import User
from schemas import LoginRequest


class AuthService:
    SECRET_KEY = os.getenv("APP_KEY")
    if not SECRET_KEY:
        raise RuntimeError("APP_KEY environment variable not set")
    
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def login_user(self, credentials: LoginRequest) -> str:
        user = self.user_repo.get_by_username(credentials.username)
        if not user or not AuthService.verify_password(credentials.password, user.password):
            raise ValueError("Invalid username or password")

        return AuthService.create_access_token(user)

    def get_current_user(self, token: str) -> User:
        token_data = self.verify_token(token)
        user = self.user_repo.get_by_id(token_data.get('userId'))
        if user is None:
            raise ValueError("Invalid token")  # User not found, just hidden
        return user 
    
    @classmethod
    def create_access_token(cls, user: User) -> str:
        expire = datetime.now() + timedelta(minutes=cls.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {
            "userId": user.id,
            "exp": expire
        }
        return jwt.encode(to_encode, cls.SECRET_KEY, algorithm=cls.ALGORITHM)

    @classmethod
    def verify_token(cls, token: str) -> dict:
        try:
            return jwt.decode(token, cls.SECRET_KEY, algorithms=[cls.ALGORITHM])
        except jwt.ExpiredSignatureError:
            raise ValueError("Token expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")

    @staticmethod
    def hash_password(password: str) -> str:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
