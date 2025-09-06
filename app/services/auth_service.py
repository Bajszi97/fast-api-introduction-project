import bcrypt
from repositories import UserRepository
from models import User
from validators import LoginRequest


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def login_user(self, credentials: LoginRequest) -> str:
        user = self.user_repo.get_by_username(credentials.username)
        if not user or not AuthService.verify_password(credentials.password, user.password):
            raise ValueError("Invalid username or password")

        return AuthService.get_token(user)

    def get_current_user(self, token: str) -> User:
        username = self.verify_token(token)
        user = self.user_repo.get_by_username(username)
        if user is None:
            raise ValueError("Invalid token")  # User not found, just hidden
        return user
    
    @staticmethod
    def get_token(user: User) -> str:
        return f"login-token-{user.username}"

    @staticmethod
    def verify_token(token: str) -> str:
        if not token.startswith("login-token-"):
            raise ValueError("Invalid token")
        return token[12:]

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
