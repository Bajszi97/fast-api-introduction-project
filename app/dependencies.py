from fastapi import Depends, HTTPException, Header, status
from services import UserService, AuthService, ProjectService
from sqlalchemy.orm import Session
from repositories import UserRepository, ProjectRepository
from db import get_db


def get_user_service(db: Session = Depends(get_db)):
    repo = UserRepository(db)
    return UserService(repo)

def get_auth_service(db: Session = Depends(get_db)):
    repo = UserRepository(db)
    return AuthService(repo)

def get_project_service(db: Session = Depends(get_db)):
    repo = ProjectRepository(db)
    return ProjectService(repo)

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