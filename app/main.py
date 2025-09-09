from dependencies import get_current_user, get_document_service, load_file_stream
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import FileResponse
from services import DocumentService
from schemas import UploadedDocument, ProjectDocumentOut
from models import User
from typing import List
from routes import auth_router, project_router


app = FastAPI()
app.include_router(auth_router)
app.include_router(project_router)


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
            path=document_service.get_document_path(document),
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