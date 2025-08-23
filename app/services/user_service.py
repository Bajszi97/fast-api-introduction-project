from models.user import User
from repositories import UserRepository
from services.auth import hash_password
from validators import CreateUserRequest


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def register_user(self, user_data: CreateUserRequest) -> User:
        existing_user = self.repo.get_by_username(user_data.username)
        if existing_user:
            raise ValueError("Username already exists")

        hashed_password = hash_password(user_data.password)
        user = self.repo.create(user_data, hashed_password)
        return user
