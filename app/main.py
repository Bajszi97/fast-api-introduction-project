from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db import get_db
from validators import CreateUserRequest, UserOut, LoginResponse, LoginRequest, ProjectOut, CreateProjectRequest
from models import User, Project, UserProject
from models.enums import Role
from services.auth import hash_password, verify_password, get_current_user
from typing import List


app = FastAPI()


@app.post("/auth", response_model=UserOut)
async def register(user: CreateUserRequest, db: Session = Depends(get_db)):
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

    return new_user


@app.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    # authenticate user
    user = db.query(User).filter(User.username == credentials.username).first()
    if not user or not verify_password(credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    token = f"login-token-{user.username}"
    return LoginResponse(
        message="Login was succesful",
        token=token,
    )


@app.post("/projects", response_model=ProjectOut)
async def create_project(
    project: CreateProjectRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # create new Project
    new_project = Project(
        name=project.name,
        description=project.description,
    )
    db.add(new_project)
    db.flush()

    # associate with admin
    admin_assoc = UserProject(
        user_id=current_user.id,
        project_id=new_project.id,
        role=Role.admin
    )

    db.add(admin_assoc)
    db.commit()

    return new_project

@app.get("/projects", response_model=List[ProjectOut])
async def list_projects(   
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):   
    return current_user.projects
    