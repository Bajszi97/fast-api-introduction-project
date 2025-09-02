from fastapi import Depends, File, HTTPException, Header, UploadFile, status
from services import UserService, AuthService, ProjectService, DocumentService
from sqlalchemy.orm import Session
from repositories import UserRepository, ProjectRepository, DocumentRepository
from db import get_db
from validators import UploadedDocument


def get_user_service(db: Session = Depends(get_db)):
    repo = UserRepository(db)
    return UserService(repo)

def get_auth_service(db: Session = Depends(get_db)):
    repo = UserRepository(db)
    return AuthService(repo)

def get_project_service(db: Session = Depends(get_db)):
    project_repo = ProjectRepository(db)
    user_repo = UserRepository(db)
    return ProjectService(project_repo, user_repo)

def get_document_service(db: Session = Depends(get_db), project_service: ProjectService = Depends(get_project_service)):
    document_repo = DocumentRepository(db)
    return DocumentService(document_repo, project_service)

def get_current_user(
    token: str = Header(...),
    db: Session = Depends(get_db)
):
    repo = UserRepository(db)
    auth_service = AuthService(repo)
    try:
        return auth_service.get_current_user(token)
    except ValueError as e:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e)
        )
    
def load_file_stream(file: UploadFile = File(...)) -> UploadedDocument:
    content = file.file.read()
    return UploadedDocument(
        filename=file.filename,
        content_type=file.content_type,
        content=content

    )
