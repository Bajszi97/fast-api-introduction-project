import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from typing import List
from dependencies import get_current_user, get_document_service, load_file_stream
from schemas import UploadedDocument, ProjectDocumentOut
from models import User
from services import DocumentService

document_router = APIRouter(prefix="/projects/{project_id}/documents", tags=["Documents"])
logger = logging.getLogger("app")

@document_router.post("", status_code=status.HTTP_201_CREATED, response_model=ProjectDocumentOut)
async def upload_project_file(
    project_id: int,
    file: UploadedDocument = Depends(load_file_stream),
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service)
):
    logger.info(f"User {current_user.id} requested to upload a document to project {project_id}.")
    try:
        new_document = document_service.create_document_for_project(project_id, file, current_user)
        logger.info(f"User {current_user.id} successfully uploaded document {new_document.id} to project {project_id}.")
        return new_document
    except LookupError:
        logger.warning(f"User {current_user.id} failed to upload document. Reason: Project {project_id} not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    except PermissionError:
        logger.warning(f"User {current_user.id} failed to upload document. Reason: Permission denied.")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to upload documents to this project")
    except ValueError:
        logger.warning(f"User {current_user.id} failed to upload document. Reason: This project already has a document with this name.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="This project already has a document with this name")
    except Exception as e:
        logger.error(f"User {current_user.id} failed to upload document. Reason: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")

@document_router.get("", response_model=List[ProjectDocumentOut])
async def list_project_documents(
    project_id: int,
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service)
):
    logger.info(f"User {current_user.id} requested to list documents for project {project_id}.")
    try:
        documents = document_service.get_documents_of_project(project_id, current_user)
        logger.info(f"User {current_user.id} successfully retrieved a list of {len(documents)} documents for project {project_id}.")
        return documents
    except LookupError:
        logger.warning(f"User {current_user.id} failed to list documents. Reason: Project {project_id} not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    except PermissionError:
        logger.warning(f"User {current_user.id} failed to list documents. Reason: Permission denied.")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to view documents for this project")
    except Exception as e:
        logger.error(f"User {current_user.id} failed to list documents. Reason: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


@document_router.get("/{document_id}", response_model=ProjectDocumentOut)
async def get_project_document(
    project_id: int,
    document_id: int,
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service)
):
    logger.info(f"User {current_user.id} requested to view document {document_id} from project {project_id}.")
    try:
        document = document_service.get_project_document(project_id, document_id, current_user)
        logger.info(f"User {current_user.id} successfully accessed document {document_id} from project {project_id}.")
        return document
    except LookupError:
        logger.warning(f"User {current_user.id} failed to access document {document_id}. Reason: Document or project not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    except PermissionError:
        logger.warning(f"User {current_user.id} failed to access document {document_id}. Reason: Access denied.")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this document")
    except Exception as e:
        logger.error(f"User {current_user.id} failed to access document {document_id}. Reason: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


@document_router.get("/{document_id}/download")
async def download_project_document(
    project_id: int,
    document_id: int,
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service)
):
    logger.info(f"User {current_user.id} requested to download document {document_id} from project {project_id}.")
    try:
        document = document_service.get_project_document(project_id, document_id, current_user)
        logger.info(f"User {current_user.id} successfully downloaded document {document_id} from project {project_id}.")
        return FileResponse(
            path=document_service.get_document_path(document),
            filename=document.filename,
            media_type=document.file_type
        )    
    except LookupError:
        logger.warning(f"User {current_user.id} failed to download document {document_id}. Reason: Document or project not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    except PermissionError:
        logger.warning(f"User {current_user.id} failed to download document {document_id}. Reason: Access denied.")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this document")
    except Exception as e:
        logger.error(f"User {current_user.id} failed to download document {document_id}. Reason: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


@document_router.put("/{document_id}", response_model=ProjectDocumentOut)
async def update_project_document(
    project_id: int,
    document_id: int,
    file: UploadedDocument = Depends(load_file_stream),
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service)
):
    logger.info(f"User {current_user.id} requested to update document {document_id} in project {project_id}.")
    try:
        updated_document = document_service.update_document_for_project(project_id, document_id, file, current_user)
        logger.info(f"User {current_user.id} successfully updated document {document_id} in project {project_id}.")
        return updated_document
    except LookupError as e:
        logger.warning(f"User {current_user.id} failed to update document {document_id}. Reason: {str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError:
        logger.warning(f"User {current_user.id} failed to update document {document_id}. Reason: Permission denied.")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to upload documents to this project")
    except ValueError:
        logger.warning(f"User {current_user.id} failed to update document {document_id}. Reason: This project already has a document with this name.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="This project already has a document with this name")
    except Exception as e:
        logger.error(f"User {current_user.id} failed to update document {document_id}. Reason: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")

@document_router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project_document(
    project_id: int,
    document_id: int,
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(get_document_service)
):
    logger.info(f"User {current_user.id} requested to delete document {document_id} from project {project_id}.")
    try:
        document_service.delete_project_document(project_id, document_id, current_user)
        logger.info(f"User {current_user.id} successfully deleted document {document_id} from project {project_id}.")
    except LookupError as e:
        logger.warning(f"User {current_user.id} failed to delete document {document_id}. Reason: {str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError:
        logger.warning(f"User {current_user.id} failed to delete document {document_id}. Reason: Permission denied.")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to delete this document")
    except Exception as e:
        logger.error(f"User {current_user.id} failed to delete document {document_id}. Reason: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")

