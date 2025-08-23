import os
from dependencies import get_user_service
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile
from fastapi.responses import FileResponse
from services import UserService
from sqlalchemy.orm import Session
from db import get_db
from validators import CreateUserRequest, UserOut, LoginResponse, LoginRequest, ProjectOut, CreateProjectRequest, AddParticipantRequest, ProjectDocumentOut
from models import User, Project, UserProject, Document
from models.enums import Role
from services.auth import verify_password, get_current_user
from typing import List


app = FastAPI()


@app.post("/auth", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(user: CreateUserRequest, service: UserService = Depends(get_user_service)):
    try:
        return service.register_user(user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))



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


@app.get("/projects/{project_id}", response_model=ProjectOut)
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    if current_user not in project.users:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this project"
        )
    return project


@app.put("/projects/{project_id}", response_model=ProjectOut)
async def update_project(
    project_id: int,
    project_update: CreateProjectRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    if current_user not in project.admins:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this project"
        )

    project.name = project_update.name
    project.description = project_update.description

    db.commit()
    db.refresh(project)

    return project


@app.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    if current_user not in project.admins:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this project"
        )

    db.delete(project)
    db.commit()


@app.post("/projects/{project_id}/participants", status_code=status.HTTP_201_CREATED)
async def add_participant(
    project_id: int,
    participant: AddParticipantRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    if current_user not in project.admins:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to add participants"
        )

    user = db.query(User).filter(User.id == participant.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    existing_assoc = db.query(UserProject).filter(
        UserProject.user_id == user.id,
        UserProject.project_id == project.id
    ).first()
    if existing_assoc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a participant"
        )

    new_assoc = UserProject(
        user_id=user.id,
        project_id=project.id,
        role=Role.participant
    )
    db.add(new_assoc)
    db.commit()
    
    return {"message": "Participant added successfully"}


@app.post("/porjects/{project_id}/documents", status_code=status.HTTP_201_CREATED, response_model=ProjectDocumentOut)
async def upload_project_file(
    project_id: int,
    file: UploadFile,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    if current_user not in project.users:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to upload documents to this project"
        )
    
    existing_file = db.query(Document).filter(Document.project_id == project.id, Document.filename == file.filename).first()
    if existing_file:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This project already has a document with this name"
        )

    new_document = Document(
        project_id=project.id,
        filename=file.filename,
        file_type=file.content_type 
    )

    db.add(new_document)
    db.commit()
    db.refresh(new_document)

    os.makedirs(Document.STORAGE_PATH.format(project_id=project.id), exist_ok=True)
    
    with open(new_document.path, "wb") as buffer:
        buffer.write(await file.read())

    return new_document



@app.get("/projects/{project_id}/documents", response_model=List[ProjectDocumentOut])
async def list_project_documents(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    if current_user not in project.users:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this project's documents"
        )
    
    return project.documents


@app.get("/projects/{project_id}/documents/{document_id}", response_model=ProjectDocumentOut)
async def get_project_document(
    project_id: int,
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    if current_user not in project.users:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this project's documents"
        )
    
    document = db.query(Document).filter(Document.id == document_id, Document.project_id == project_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project's document not found"
        )
    
    return document


@app.get("/projects/{project_id}/documents/{document_id}/download")
async def download_project_document(
    project_id: int,
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    if current_user not in project.users:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this project's documents"
        )
    
    document = db.query(Document).filter(Document.id == document_id, Document.project_id == project_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project's document not found"
        )
    
    return FileResponse(
        path=document.path,
        filename=document.filename,
        media_type=document.file_type
    )


@app.put("/projects/{project_id}/documents/{document_id}", response_model=ProjectDocumentOut)
async def update_project_document(
    project_id: int,
    document_id: int,
    file: UploadFile,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    if current_user not in project.users:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this project's documents"
        )
    
    document = db.query(Document).filter(Document.id == document_id, Document.project_id == project_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project's document not found"
        )
    
    os.remove(document.path)
    
    if file.filename is not None:
        document.filename=file.filename
    if file.content_type is not None:
        document.file_type=file.content_type

    db.commit()
    db.refresh(project)

    with open(document.path, "wb") as buffer:
        buffer.write(await file.read())
    
    return document


@app.delete("/projects/{project_id}/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project_document(
    project_id: int,
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    if current_user not in project.users:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this project's documents"
        )
    
    document = db.query(Document).filter(Document.id == document_id, Document.project_id == project_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project's document not found"
        )

    try:
        os.remove(document.path)
    except FileNotFoundError:
        pass 

    db.delete(document)
    db.commit()