import bcrypt
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from models import User
from db import get_db

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )

def get_current_user(token: str = Header(...), db: Session = Depends(get_db)) -> User:
    if not token.startswith("login-token-"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    username = token[12:]
    user = db.query(User).filter(User.username == username).first()

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    return user