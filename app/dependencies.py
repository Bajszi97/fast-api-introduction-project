# app/api/dependencies.py
from fastapi import Depends, Header
from services import UserService
from sqlalchemy.orm import Session
from repositories import UserRepository
from db import get_db


def get_user_service(db: Session = Depends(get_db)):
    repo = UserRepository(db)
    return UserService(repo)