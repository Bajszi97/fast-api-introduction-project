from models import Project, Document, User

def make_user(id: int = 1, username: str = "testuser", password: str = "hashed_password") -> User:
    return User(id=id, username=username, password=password)

def make_project(id: int = 1, name: str = "Test Project", description: str|None = "Describing test project.") -> Project:
    return Project(id=id, name=name, description=description)

def make_document(id: int = 1, filename: str = "test.txt", file_type: str = "text/plain") -> Document:
    return Document(id=id, filename=filename, file_type=file_type)