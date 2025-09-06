from sqlalchemy import desc
from models import Project, Document, User
from repositories import UserRepository
from services.auth_service import AuthService
from validators import CreateProjectRequest, CreateUserRequest
from sqlalchemy.orm import Session

def make_user(id: int = 1, username: str = "testuser", password: str = "hashed_password") -> User:
    return User(id=id, username=username, password=password)

def make_project(id: int = 1, name: str = "Test Project", description: str|None = "Describing test project.") -> Project:
    return Project(id=id, name=name, description=description)

def make_document(id: int = 1, filename: str = "test.txt", file_type: str = "text/plain") -> Document:
    return Document(id=id, filename=filename, file_type=file_type)

def make_register_request(username: str = "testuser", password: str = "strongtestpassword") -> CreateUserRequest:
    return CreateUserRequest(username=username, password=password, password_confirm=password)

def make_project_request(name: str = "testproject", description: str = "Describing the test project") -> CreateProjectRequest:
    return CreateProjectRequest(name=name, description=description)

def create_user(db: Session, username: str = "testuser", password: str = "strongtestpassword"):
    user_repo = UserRepository(db)
    user_data = make_register_request(username=username, password=password)
    hashed_password = AuthService.hash_password(user_data.password)

    return user_repo.create(user_data=user_data, hashed_password=hashed_password)