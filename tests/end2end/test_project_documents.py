
from fastapi.testclient import TestClient
from typing import Callable
from models import User
from factories import make_document_request, make_project_request
from models.document import Document
from models.project import Project
from services.auth_service import AuthService
from conftest import document_factory
from schemas import ProjectDocumentOut

def test_user_can_upload_document_to_their_project(
    client: TestClient,
    user_factory: Callable[..., User],
    project_factory: Callable[..., Project]
):
    """
    Test that a user can successfully upload a document to a project they own.
    """
    user = user_factory()
    headers = {"token": AuthService.create_access_token(user)}
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
    headers = {"token": AuthService.create_access_token(non_owner)}
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
    headers = {"token": AuthService.create_access_token(user)}
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
    headers = {"token": AuthService.create_access_token(user)}
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
    headers = {"token": AuthService.create_access_token(user)}
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
    headers = {"token": AuthService.create_access_token(user)}
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
    headers = {"token": AuthService.create_access_token(non_owner)}
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
    headers = {"token": AuthService.create_access_token(user)}
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


def test_user_can_get_their_project_document(
    client: TestClient,
    user_factory: Callable[..., User],
    project_factory: Callable[..., Project],
    document_factory: Callable[..., Document]
):
    """
    Test that a user can successfully retrieve a specific document from a project they own.
    """
    user = user_factory()
    headers = {"token": AuthService.create_access_token(user)}
    project = project_factory(user=user)
    document = document_factory(project=project, filename="my_document.txt")

    response = client.get(f"/projects/{project.id}/documents/{document.id}", headers=headers)

    assert response.status_code == 200
    retrieved_document = ProjectDocumentOut(**response.json())
    assert retrieved_document.id == document.id
    assert retrieved_document.filename == "my_document.txt"


def test_user_cannot_get_another_users_project_document(
    client: TestClient,
    user_factory: Callable[..., User],
    project_factory: Callable[..., Project],
    document_factory: Callable[..., Document]
):
    """
    Test that a user cannot retrieve a document from a project that belongs to a different user.
    """
    owner = user_factory(username="owner")
    non_owner = user_factory(username="non_owner")
    headers = {"token": AuthService.create_access_token(non_owner)}
    project_for_owner = project_factory(user=owner)
    document_for_owner = document_factory(project=project_for_owner)

    response = client.get(f"/projects/{project_for_owner.id}/documents/{document_for_owner.id}", headers=headers)

    assert response.status_code == 403


def test_get_document_from_non_existent_project(
    client: TestClient,
    user_factory: Callable[..., User]
):
    """
    Test that an attempt to retrieve a document from a non-existent project returns a 404.
    """
    user = user_factory()
    headers = {"token": AuthService.create_access_token(user)}
    non_existent_project_id = 999
    non_existent_document_id = 1

    response = client.get(
        f"/projects/{non_existent_project_id}/documents/{non_existent_document_id}",
        headers=headers
    )

    assert response.status_code == 404


def test_get_non_existent_document(
    client: TestClient,
    user_factory: Callable[..., User],
    project_factory: Callable[..., Project]
):
    """
    Test that an attempt to retrieve a non-existent document from an existing project returns a 404.
    """
    user = user_factory()
    headers = {"token": AuthService.create_access_token(user)}
    project = project_factory(user=user)
    non_existent_document_id = 999

    response = client.get(
        f"/projects/{project.id}/documents/{non_existent_document_id}",
        headers=headers
    )

    assert response.status_code == 404


def test_unauthenticated_user_cannot_get_document(
    client: TestClient,
    user_factory: Callable[..., User],
    project_factory: Callable[..., Project],
    document_factory: Callable[..., Document]
):
    """
    Test that an unauthenticated user cannot get a document from any project.
    """
    user = user_factory()
    project = project_factory(user=user)
    document = document_factory(project=project)

    response = client.get(f"/projects/{project.id}/documents/{document.id}") # No auth token

    assert response.status_code == 401

def test_user_can_download_their_project_document(
    client: TestClient,
    user_factory: Callable[..., User],
    project_factory: Callable[..., Project],
    document_factory: Callable[..., Document]
):
    """
    Test that a user can successfully download a specific document from a project they own.
    """
    user = user_factory()
    headers = {"token": AuthService.create_access_token(user)}
    project = project_factory(user=user)
    file_content = "This is the content of the uploaded file."
    document = document_factory(project=project, content=file_content)

    response = client.get(f"/projects/{project.id}/documents/{document.id}/download", headers=headers)
    
    assert response.status_code == 200
    assert response.content == file_content.encode()


def test_user_can_update_their_project_document(
    client: TestClient,
    user_factory: Callable[..., User],
    project_factory: Callable[..., Project],
    document_factory: Callable[..., Document]
):
    """
    Test that a user can successfully update a specific document they own.
    """
    user = user_factory()
    headers = {"token": AuthService.create_access_token(user)}
    project = project_factory(user=user)
    document = document_factory(project=project)
    new_filename = "new-file.txt"
    updated_file_content = b"This is the new content of the document."
    updated_file = make_document_request(filename=new_filename, file_content=updated_file_content)
    
    response = client.put(
        f"/projects/{project.id}/documents/{document.id}",
        files=updated_file,
        headers=headers
    )

    assert response.status_code == 200
    updated_doc = ProjectDocumentOut(**response.json())
    assert updated_doc.filename == new_filename


def test_user_cannot_update_another_users_project_document(
    client: TestClient,
    user_factory: Callable[..., User],
    project_factory: Callable[..., Project],
    document_factory: Callable[..., Document]
):
    """
    Test that a user cannot update a document belonging to another user.
    """
    owner = user_factory(username="owner")
    non_owner = user_factory(username="non_owner")
    headers = {"token": AuthService.create_access_token(non_owner)}
    project_for_owner = project_factory(user=owner)
    document_for_owner = document_factory(project=project_for_owner)
    new_filename = "new-file.txt"
    updated_file_content = b"This is the new content of the document."
    updated_file = make_document_request(filename=new_filename, file_content=updated_file_content)

    response = client.put(
        f"/projects/{project_for_owner.id}/documents/{document_for_owner.id}",
        files=updated_file,
        headers=headers
    )

    assert response.status_code == 403


def test_update_document_in_non_existent_project(
    client: TestClient,
    user_factory: Callable[..., User]
):
    """
    Test that an attempt to update a document in a non-existent project returns a 404.
    """
    user = user_factory()
    headers = {"token": AuthService.create_access_token(user)}
    non_existent_project_id = 999
    non_existent_document_id = 1
    new_filename = "new-file.txt"
    updated_file_content = b"This is the new content of the document."
    updated_file = make_document_request(filename=new_filename, file_content=updated_file_content)

    response = client.put(
        f"/projects/{non_existent_project_id}/documents/{non_existent_document_id}",
        files=updated_file,
        headers=headers
    )

    assert response.status_code == 404


def test_update_non_existent_document(
    client: TestClient,
    user_factory: Callable[..., User],
    project_factory: Callable[..., Project]
):
    """
    Test that an attempt to update a non-existent document returns a 404.
    """
    user = user_factory()
    headers = {"token": AuthService.create_access_token(user)}
    project = project_factory(user=user)
    non_existent_document_id = 999
    new_filename = "new-file.txt"
    updated_file_content = b"This is the new content of the document."
    updated_file = make_document_request(filename=new_filename, file_content=updated_file_content)
    
    response = client.put(
        f"/projects/{project.id}/documents/{non_existent_document_id}",
        files=updated_file,
        headers=headers
    )

    assert response.status_code == 404


def test_update_document_to_existing_name(
    client: TestClient,
    user_factory: Callable[..., User],
    project_factory: Callable[..., Project],
    document_factory: Callable[..., Document]
):
    """
    Test that an attempt to update a document to a name that already exists in the same project returns a 404.
    """
    user = user_factory()
    headers = {"token": AuthService.create_access_token(user)}
    project = project_factory(user=user)
    document_to_update = document_factory(project=project, filename="original.txt")
    existing_document = document_factory(project=project, filename="existing.txt")
    new_filename = existing_document.filename
    updated_file_content = b"This is the new content of the document."
    updated_file = make_document_request(filename=new_filename, file_content=updated_file_content)
    
    response = client.put(
        f"/projects/{project.id}/documents/{document_to_update.id}",
        files=updated_file,
        headers=headers
    )
    
    assert response.status_code == 404


def test_unauthenticated_user_cannot_update_document(
    client: TestClient,
    user_factory: Callable[..., User],
    project_factory: Callable[..., Project],
    document_factory: Callable[..., Document]
):
    """
    Test that an unauthenticated user cannot update any document.
    """
    user = user_factory()
    project = project_factory(user=user)
    document = document_factory(project=project)
    new_filename = "new-filename.txt"
    updated_file_content = b"This is the new content of the document."
    updated_file = make_document_request(filename=new_filename, file_content=updated_file_content)

    response = client.put(f"/projects/{project.id}/documents/{document.id}", files=updated_file) # No auth token

    assert response.status_code == 401

def test_user_can_delete_their_project_document(
    client: TestClient,
    user_factory: Callable[..., User],
    project_factory: Callable[..., Project],
    document_factory: Callable[..., Document]
):
    """
    Test that a user can successfully delete a specific document from a project they own.
    """
    user = user_factory()
    headers = {"token": AuthService.create_access_token(user)}
    project = project_factory(user=user)
    document = document_factory(project=project)

    response = client.delete(f"/projects/{project.id}/documents/{document.id}", headers=headers)

    assert response.status_code == 204
    assert not response.content 

    get_response = client.get(f"/projects/{project.id}/documents/{document.id}", headers=headers)
    assert get_response.status_code == 404


def test_user_cannot_delete_another_users_project_document(
    client: TestClient,
    user_factory: Callable[..., User],
    project_factory: Callable[..., Project],
    document_factory: Callable[..., Document]
):
    """
    Test that a user cannot delete a document from a project that belongs to a different user.
    """
    owner = user_factory(username="owner")
    non_owner = user_factory(username="non_owner")
    headers = {"token": AuthService.create_access_token(non_owner)}
    project_for_owner = project_factory(user=owner)
    document_for_owner = document_factory(project=project_for_owner)

    response = client.delete(
        f"/projects/{project_for_owner.id}/documents/{document_for_owner.id}", 
        headers=headers
    )

    assert response.status_code == 403


def test_delete_document_from_non_existent_project(
    client: TestClient,
    user_factory: Callable[..., User]
):
    """
    Test that an attempt to delete a document from a non-existent project returns a 404.
    """
    user = user_factory()
    headers = {"token": AuthService.create_access_token(user)}
    non_existent_project_id = 999
    non_existent_document_id = 1

    response = client.delete(
        f"/projects/{non_existent_project_id}/documents/{non_existent_document_id}",
        headers=headers
    )

    assert response.status_code == 404


def test_delete_non_existent_document(
    client: TestClient,
    user_factory: Callable[..., User],
    project_factory: Callable[..., Project]
):
    """
    Test that an attempt to delete a non-existent document from an existing project returns a 404.
    """
    user = user_factory()
    headers = {"token": AuthService.create_access_token(user)}
    project = project_factory(user=user)
    non_existent_document_id = 999

    response = client.delete(
        f"/projects/{project.id}/documents/{non_existent_document_id}",
        headers=headers
    )

    assert response.status_code == 404


def test_unauthenticated_user_cannot_delete_document(
    client: TestClient,
    user_factory: Callable[..., User],
    project_factory: Callable[..., Project],
    document_factory: Callable[..., Document]
):
    """
    Test that an unauthenticated user cannot delete a document from any project.
    """
    user = user_factory()
    project = project_factory(user=user)
    document = document_factory(project=project)

    response = client.delete(f"/projects/{project.id}/documents/{document.id}") # No auth token

    assert response.status_code == 401
