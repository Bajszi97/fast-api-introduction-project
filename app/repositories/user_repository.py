from sqlalchemy.orm import Session
from models import User
from schemas import CreateUserRequest


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_username(self, username):
        return self.db.query(User).filter(User.username == username).first()
    
    def get_by_id(self, id):
        return self.db.query(User).filter(User.id == id).first()

    def create(self, user_data: CreateUserRequest, hashed_password: str):
        new_user = User(
            username=user_data.username,
            password=hashed_password,
        )
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user
