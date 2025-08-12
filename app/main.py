from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db import get_db
from validators import CreateUserRequest, CreateUserResponse
from models import User
from services.auth import hash_password

app = FastAPI()

@app.post("/auth", response_model=CreateUserResponse)
async def create_user(user: CreateUserRequest, db: Session = Depends(get_db)):

    # check if username exists
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )

    # create new User
    new_user = User(
        username=user.username,
        password=hash_password(user.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return CreateUserResponse(
        id=new_user.id,
        username=new_user.username,
        created_at=new_user.created_at.isoformat(),
    )
