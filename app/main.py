import os
from dependencies import get_user_service, get_current_user, get_auth_service, get_project_service, get_document_service, load_file_stream
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile
from fastapi.responses import FileResponse
from services import UserService, ProjectService, DocumentService
from sqlalchemy.orm import Session
from db import get_db
from validators import CreateUserRequest, UploadedDocument, UserOut, LoginResponse, LoginRequest, ProjectOut, CreateProjectRequest, AddParticipantRequest, ProjectDocumentOut
from models import User, Project, UserProject, Document
from models.enums import Role
from typing import List
from services import AuthService


app = FastAPI()


@app.post("/auth", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(user: CreateUserRequest, service: UserService = Depends(get_user_service)):
    try:
        return service.register_user(user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest, service: AuthService = Depends(get_auth_service)):
    try:
        token = service.login_user(credentials)
        return LoginResponse(
            message="Login was succesful",
            token=token,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@app.post("/projects", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: CreateProjectRequest,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service)
):
    return project_service.create_for_user(project, current_user)


@app.get("/projects", response_model=List[ProjectOut])
async def list_projects(
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service)
):
    return project_service.get_user_projects(current_user)


@app.get("/projects/{project_id}", response_model=ProjectOut)
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service)
):  
    try:
        return project_service.get_project_for_user(project_id, current_user)
    except LookupError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this project")


@app.put("/projects/{project_id}", response_model=ProjectOut)
async def update_project(
    project_id: int,
    project_update: CreateProjectRequest,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service)
):
    try:
        return project_service.update_project_for_user(project_id, project_update, current_user)
    except LookupError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to update this project")



@app.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service)
):
    try:
        return project_service.delete_project_for_user(project_id, current_user)
    except LookupError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to delete this project")


@app.post("/projects/{project_id}/participants", status_code=status.HTTP_201_CREATED)
async def add_participant(
    project_id: int,
    participant: AddParticipantRequest,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service)
):
    try:
        project_service.add_participant(project_id, participant.user_id, current_user)
    except LookupError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to add participants")
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except RuntimeError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is already a participant")

    return {"message": "Participant added successfully"}


@app.post("/porjects/{project_id}/documents", status_code=status.HTTP_201_CREATED, response_model=ProjectDocumentOut)
async def upload_project_file(
    project_id: int,
    file: UploadedDocument = Depends(load_file_stream),
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service)
):
    try:
        return document_service.create_document_for_project(project_id, file, current_user)
    except LookupError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to upload documents to this project")
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="This project already has a document with this name")



@app.get("/projects/{project_id}/documents", response_model=List[ProjectDocumentOut])
async def list_project_documents(
    project_id: int,
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service)
):
    try:
        return document_service.get_documents_of_project(project_id, current_user)
    except LookupError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this project's documents")


@app.get("/projects/{project_id}/documents/{document_id}", response_model=ProjectDocumentOut)
async def get_project_document(
    project_id: int,
    document_id: int,
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service)
):
    try:
        return document_service.get_project_document(project_id, document_id, current_user)
    except LookupError as e: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to access this project's documents")


@app.get("/projects/{project_id}/documents/{document_id}/download")
async def download_project_document(
    project_id: int,
    document_id: int,
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service)
):
    try:
        document = document_service.get_project_document(project_id, document_id, current_user)
        return FileResponse(
            path=document.path,
            filename=document.filename,
            media_type=document.file_type
        )
    except LookupError as e: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to access this project's documents")



@app.put("/projects/{project_id}/documents/{document_id}", response_model=ProjectDocumentOut)
async def update_project_document(
    project_id: int,
    document_id: int,
    file: UploadedDocument = Depends(load_file_stream),
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service)
):
    try:
        return document_service.update_document_for_project(project_id, document_id, file, current_user)
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to upload documents to this project")
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="This project already has a document with this name")


@app.delete("/projects/{project_id}/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project_document(
    project_id: int,
    document_id: int,
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service)
):
    try:
        return document_service.delete_project_document(project_id, document_id, current_user)
    except LookupError as e: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to delete this project's documents")