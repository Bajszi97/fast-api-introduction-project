
from fastapi.testclient import TestClient
from typing import Callable
from models import User
from factories import make_document_request, make_project_request
from models.document import Document
from models.project import Project
from services.auth_service import AuthService
from conftest import document_factory
from validators import ProjectDocumentOut

def test_user_can_upload_document_to_their_project(
    client: TestClient,
    user_factory: Callable[..., User],
    project_factory: Callable[..., Project]
):
    """
    Test that a user can successfully upload a document to a project they own.
    """
    user = user_factory()
    headers = {"token": AuthService.get_token(user)}
    project = project_factory(user=user, name="Project with Documents")
    files = make_document_request()

    response = client.post(
        f"/porjects/{project.id}/documents",
        files=files,
        headers=headers
    )

    assert response.status_code == 201
    docuemnt = ProjectDocumentOut(**response.json())
    assert docuemnt.filename == "test_document.txt"


def test_user_cannot_upload_to_another_users_project(
    client: TestClient,
    user_factory: Callable[..., User],
    project_factory: Callable[..., Project]
):
    """
    Test that a user cannot upload a document to a project belonging to another user.
    """
    owner = user_factory(username="owner")
    non_owner = user_factory(username="non_owner")
    headers = {"token": AuthService.get_token(non_owner)}
    project = project_factory(user=owner)
    files = make_document_request()
    
    response = client.post(
        f"/porjects/{project.id}/documents",
        files=files,
        headers=headers
    )

    assert response.status_code == 403
    assert "You do not have permission to upload documents to this project" in response.json()["detail"]


def test_upload_to_non_existent_project(
    client: TestClient,
    user_factory: Callable[..., User]
):
    """
    Test that an attempt to upload a document to a non-existent project returns a 404.
    """
    user = user_factory()
    headers = {"token": AuthService.get_token(user)}
    non_existent_project_id = 999
    files = make_document_request()

    response = client.post(
        f"/porjects/{non_existent_project_id}/documents",
        files=files,
        headers=headers
    )

    assert response.status_code == 404
    assert "Project not found" in response.json()["detail"]


def test_upload_document_with_existing_name(
    client: TestClient,
    user_factory: Callable[..., User],
    project_factory: Callable[..., Project]
):
    """
    Test that an attempt to upload a document with a name that already exists returns a 404.
    """
    user = user_factory()
    headers = {"token": AuthService.get_token(user)}
    project = project_factory(user=user, name="Project with existing file")
    files = make_document_request()
    
    # first try 
    client.post(f"/porjects/{project.id}/documents", files=files, headers=headers)

    # second try
    response = client.post(
        f"/porjects/{project.id}/documents",
        files=files,
        headers=headers
    )
    
    assert response.status_code == 404


def test_unauthenticated_user_cannot_upload_document(
    client: TestClient,
    user_factory: Callable[..., User],
    project_factory: Callable[..., Project]
):
    """
    Test that an unauthenticated user cannot upload documents.
    """
    user = user_factory()
    project = project_factory(user=user)
    files = make_document_request()
    
    response = client.post(f"/porjects/{project.id}/documents", files=files) # No auth token

    assert response.status_code == 401


def test_user_can_list_project_documents(
    client: TestClient, 
    user_factory: Callable[..., User], 
    project_factory: Callable[..., Project],
    document_factory: Callable[..., Document]
):
    """
    Test that a user can successfully retrieve a list of documents for a project they own.
    """
    user = user_factory()
    headers = {"token": AuthService.get_token(user)}
    project = project_factory(user=user, name="Project with documents")
    count = 5
    documents = [document_factory(project, filename=f"document-{n}.txt") for n in range(count)]
    
    response = client.get(f"/projects/{project.id}/documents", headers=headers)
    
    assert response.status_code == 200
    documents = [ProjectDocumentOut(**doc) for doc in response.json()]
    assert len(documents) == count
    assert documents[0].filename == "document-0.txt"


def test_user_gets_no_documents_if_none_exist(
    client: TestClient, 
    user_factory: Callable[..., User], 
    project_factory: Callable[..., Project]
):
    """
    Test that a user gets an empty list if there are no documents in the project.
    """
    user = user_factory()
    headers = {"token": AuthService.get_token(user)}
    project = project_factory(user=user)

    response = client.get(f"/projects/{project.id}/documents", headers=headers)
    
    assert response.status_code == 200
    assert response.json() == []


def test_user_cannot_list_another_users_project_documents(
    client: TestClient,
    user_factory: Callable[..., User],
    project_factory: Callable[..., Project]
):
    """
    Test that a user cannot retrieve documents from a project that belongs to a different user.
    """
    owner = user_factory(username="owner")
    non_owner = user_factory(username="non_owner")
    headers = {"token": AuthService.get_token(non_owner)}
    project = project_factory(user=owner)
    
    response = client.get(f"/projects/{project.id}/documents", headers=headers)

    assert response.status_code == 403


def test_list_documents_for_non_existent_project(
    client: TestClient,
    user_factory: Callable[..., User]
):
    """
    Test that an attempt to list documents for a non-existent project returns a 404.
    """
    user = user_factory()
    headers = {"token": AuthService.get_token(user)}
    non_existent_project_id = 999
    
    response = client.get(f"/projects/{non_existent_project_id}/documents", headers=headers)

    assert response.status_code == 404


def test_unauthenticated_user_cannot_list_documents(
    client: TestClient,
    user_factory: Callable[..., User],
    project_factory: Callable[..., Project]
):
    """
    Test that an unauthenticated user cannot list documents for any project.
    """
    user = user_factory()
    project = project_factory(user=user)

    response = client.get(f"/projects/{project.id}/documents") # No auth token

    assert response.status_code == 401
