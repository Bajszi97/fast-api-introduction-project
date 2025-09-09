import io
from typing import List
from models import Project, Document, User
from repositories import UserRepository, ProjectRepository, DocumentRepository
from services.auth_service import AuthService
from validators import CreateProjectRequest, CreateUserRequest, UploadedDocument
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

def make_document_request(filename: str = "test_document.txt", file_content = b"This is the content of the test document.", file_type: str = "text/plain"):
    return {"file": (filename, io.BytesIO(file_content), file_type)}


def create_user(db: Session, username: str = "testuser", password: str = "strongtestpassword"):
    user_repo = UserRepository(db)
    user_data = make_register_request(username=username, password=password)
    hashed_password = AuthService.hash_password(user_data.password)

    return user_repo.create(user_data=user_data, hashed_password=hashed_password)

def create_project(db: Session, user: User, name: str = "testproject", description: str = "Describing the test project", participants: List[User] = []):
    project_repo = ProjectRepository(db)
    project_data = make_project_request(name=name, description=description)
    project = project_repo.create_for_user(project_data=project_data, user=user)
    for participant in participants:
        project_repo.add_participant(project=project, participant=participant) 
    return project

def create_document(
    db: Session,
    project: Project,
    filename: str = "test_file.txt",
    content: str = "Text file content.",
    file_type: str = "text/plain"
):
    document_repo = DocumentRepository(db)
    document_data = UploadedDocument(
        filename=filename,
        content=content.encode(),
        content_type=file_type
    )
    return document_repo.create_project_document(project.id, document_data)

