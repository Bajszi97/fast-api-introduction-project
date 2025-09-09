from fastapi.testclient import TestClient
from typing import Callable
from sqlalchemy.orm import Session
from models import User
from factories import make_project_request
from models.project import Project
from services.auth_service import AuthService
from schemas import ProjectOut


def test_user_can_create_project(client: TestClient, user_factory: Callable[..., User]):
    """
    Test that a user can create a project.
    """
    user = user_factory()
    headers = {"token": AuthService.create_access_token(user)}
    project_request = make_project_request() 

    response = client.post("/projects", json=project_request.model_dump(), headers=headers)
    
    assert response.status_code == 201
    project = ProjectOut(**response.json())
    assert project.name == project_request.name


def test_only_logged_in_user_can_create_project(client: TestClient, user_factory: Callable[..., User]):
    """
    Test that a user can create a project.
    """
    user = user_factory()
    project_request = make_project_request() 

    response = client.post("/projects", json=project_request.model_dump()) # No auth token
    
    assert response.status_code == 401


def test_project_cannot_be_created_without_name(client: TestClient, user_factory: Callable[..., User]):
    """
    Test that a user can create a project.
    """
    user = user_factory()
    headers = {"token": AuthService.create_access_token(user)}
    project_request = {
        "name": "",
    }

    response = client.post("/projects", json=project_request, headers=headers)
    
    assert response.status_code == 422

def test_user_can_get_their_projects(
        client: TestClient,
        user_factory: Callable[..., User],
        project_factory: Callable[..., Project],
    ):
    """
    Test that a user can retrieve a list of their projects.
    """
    user = user_factory()
    headers = {"token": AuthService.create_access_token(user)}
    project_count = 5
    projects = [project_factory(user=user, name=f"Test Project {n}") for n in range(project_count)]

    response = client.get("/projects", headers=headers)
    
    assert response.status_code == 200
    projects = [ProjectOut(**project) for project in response.json()]
    assert len(projects) == project_count
    assert projects[0].name == "Test Project 0"


def test_user_gets_no_projects_if_none_exist(client: TestClient, user_factory: Callable[..., User]):
    """
    Test that a user gets an empty list if they have no projects.
    """
    user = user_factory()
    headers = {"token": AuthService.create_access_token(user)}

    response = client.get("/projects", headers=headers)

    assert response.status_code == 200
    assert response.json() == []

def test_unauthenticated_user_cannot_get_projects(client: TestClient):
    """
    Test that an unauthenticated user cannot access the projects endpoint.
    """
    response = client.get("/projects")
    
    assert response.status_code == 401


def test_user_can_get_their_project(
    client: TestClient, 
    user_factory: Callable[..., User], 
    project_factory: Callable[..., Project]
):
    """
    Test that a user can retrieve a specific project they own.
    """
    user = user_factory()
    headers = {"token": AuthService.create_access_token(user)}
    project = project_factory(user=user, name="My Project")
    
    response = client.get(f"/projects/{project.id}", headers=headers)

    assert response.status_code == 200
    retrieved_project = ProjectOut(**response.json())
    assert retrieved_project.id == project.id
    assert retrieved_project.name == "My Project"


def test_user_cannot_get_another_users_project(
    client: TestClient, 
    user_factory: Callable[..., User], 
    project_factory: Callable[..., Project]
):
    """
    Test that a user cannot retrieve a project that belongs to a different user.
    """
    user1 = user_factory(username="user1")
    user2 = user_factory(username="user2")
    headers = {"token": AuthService.create_access_token(user1)}
    project_for_user2 = project_factory(user=user2, name="Another User's Project")

    response = client.get(f"/projects/{project_for_user2.id}", headers=headers)

    assert response.status_code == 403


def test_get_non_existent_project(
    client: TestClient, 
    user_factory: Callable[..., User]
):
    """
    Test that an attempt to retrieve a non-existent project returns a 404.
    """
    user = user_factory()
    headers = {"token": AuthService.create_access_token(user)}
    non_existent_project_id = 999
    
    response = client.get(f"/projects/{non_existent_project_id}", headers=headers)

    assert response.status_code == 404


def test_unauthenticated_user_cannot_get_project(
    client: TestClient, 
    user_factory: Callable[..., User], 
    project_factory: Callable[..., Project]
):
    """
    Test that an unauthenticated user cannot access a specific project.
    """
    user = user_factory()
    project = project_factory(user=user, name="My Project")

    response = client.get(f"/projects/{project.id}") # No auth token

    assert response.status_code == 401


def test_user_can_update_their_project(
    client: TestClient,
    user_factory: Callable[..., User],
    project_factory: Callable[..., Project]
):
    """
    Test that a user can successfully update a project they own.
    """
    user = user_factory()
    headers = {"token": AuthService.create_access_token(user)}
    original_project = project_factory(user=user, name="Old Project Name", description="Old description")
    updated_data = make_project_request(name="Updated Project Name", description="New description for the project")

    response = client.put(f"/projects/{original_project.id}", json=updated_data.model_dump(), headers=headers)
    
    assert response.status_code == 200
    updated_project = ProjectOut(**response.json())
    assert updated_project.id == original_project.id
    assert updated_project.name == "Updated Project Name"
    assert updated_project.description == "New description for the project"


def test_user_cannot_update_another_users_project(
    client: TestClient,
    user_factory: Callable[..., User],
    project_factory: Callable[..., Project]
):
    """
    Test that a user cannot update a project that belongs to another user.
    """
    user1 = user_factory(username="user1")
    user2 = user_factory(username="user2")
    headers = {"token": AuthService.create_access_token(user1)}
    project_for_user2 = project_factory(user=user2, name="Project to be hijacked")
    updated_data = make_project_request(name="Updated Project Name", description="New description for the project")

    response = client.put(f"/projects/{project_for_user2.id}", json=updated_data.model_dump(), headers=headers)

    assert response.status_code == 403


def test_update_non_existent_project(
    client: TestClient, 
    user_factory: Callable[..., User]
):
    """
    Test that an attempt to update a non-existent project returns a 404.
    """
    user = user_factory()
    headers = {"token": AuthService.create_access_token(user)}
    non_existent_project_id = 999
    updated_data = make_project_request(name="Updated Project Name", description="New description for the project")

    response = client.put(f"/projects/{non_existent_project_id}", json=updated_data.model_dump(), headers=headers)

    assert response.status_code == 404


def test_unauthenticated_user_cannot_update_project(
    client: TestClient, 
    user_factory: Callable[..., User], 
    project_factory: Callable[..., Project]
):
    """
    Test that an unauthenticated user cannot update any project.
    """
    user = user_factory()
    project = project_factory(user=user, name="My Project")
    updated_data = make_project_request(name="Updated Project Name", description="New description for the project")

    response = client.put(f"/projects/{project.id}", json=updated_data.model_dump()) # No auth token

    assert response.status_code == 401


def test_user_can_delete_their_project(
    client: TestClient,
    user_factory: Callable[..., User],
    project_factory: Callable[..., Project]
):
    """
    Test that a user can successfully delete a project they own.
    """
    user = user_factory()
    headers = {"token": AuthService.create_access_token(user)}
    project = project_factory(user=user, name="Project to be deleted")

    response = client.delete(f"/projects/{project.id}", headers=headers)
    
    assert response.status_code == 204
    assert not response.content

    # Verify the project is actually deleted by trying to retrieve it
    get_response = client.get(f"/projects/{project.id}", headers=headers)
    assert get_response.status_code == 404


def test_user_cannot_delete_another_users_project(
    client: TestClient,
    user_factory: Callable[..., User],
    project_factory: Callable[..., Project]
):
    """
    Test that a user cannot delete a project that belongs to another user.
    """
    user1 = user_factory(username="user1")
    user2 = user_factory(username="user2")
    headers = {"token": AuthService.create_access_token(user1)}
    project_for_user2 = project_factory(user=user2, name="Project to be hijacked")
    
    response = client.delete(f"/projects/{project_for_user2.id}", headers=headers)

    assert response.status_code == 403


def test_delete_non_existent_project(
    client: TestClient, 
    user_factory: Callable[..., User]
):
    """
    Test that an attempt to delete a non-existent project returns a 404.
    """
    user = user_factory()
    headers = {"token": AuthService.create_access_token(user)}
    non_existent_project_id = 999
    
    response = client.delete(f"/projects/{non_existent_project_id}", headers=headers)

    assert response.status_code == 404


def test_unauthenticated_user_cannot_delete_project(
    client: TestClient, 
    user_factory: Callable[..., User], 
    project_factory: Callable[..., Project]
):
    """
    Test that an unauthenticated user cannot delete any project.
    """
    user = user_factory()
    project = project_factory(user=user, name="My Project")

    response = client.delete(f"/projects/{project.id}") # No auth token

    assert response.status_code == 401


def test_project_owner_can_add_participant(
    client: TestClient,
    user_factory: Callable[..., User],
    project_factory: Callable[..., Project]
):
    """
    Test that the project owner can successfully add another user as a participant.
    """
    owner = user_factory(username="owner")
    participant_to_add = user_factory(username="new_participant")
    headers = {"token": AuthService.create_access_token(owner)}
    project = project_factory(user=owner)

    response = client.post(
        f"/projects/{project.id}/participants",
        json={"user_id": participant_to_add.id},
        headers=headers
    )

    assert response.status_code == 201
    assert response.json()["message"] == "Participant added successfully"


def test_non_owner_cannot_add_participant(
    client: TestClient,
    user_factory: Callable[..., User],
    project_factory: Callable[..., Project]
):
    """
    Test that a non-owner cannot add a participant to a project.
    """
    owner = user_factory(username="owner")
    non_owner = user_factory(username="non_owner")
    participant_to_add = user_factory(username="new_participant")
    headers = {"token": AuthService.create_access_token(non_owner)}
    project = project_factory(user=owner)

    response = client.post(
        f"/projects/{project.id}/participants",
        json={"user_id": participant_to_add.id},
        headers=headers
    )

    assert response.status_code == 403


def test_add_participant_to_non_existent_project(
    client: TestClient,
    user_factory: Callable[..., User]
):
    """
    Test that an attempt to add a participant to a non-existent project returns a 404.
    """
    user = user_factory()
    headers = {"token": AuthService.create_access_token(user)}
    non_existent_project_id = 999
    
    response = client.post(
        f"/projects/{non_existent_project_id}/participants",
        json={"user_id": user.id},
        headers=headers
    )

    assert response.status_code == 404


def test_add_non_existent_user_as_participant(
    client: TestClient,
    user_factory: Callable[..., User],
    project_factory: Callable[..., Project]
):
    """
    Test that an attempt to add a non-existent user as a participant returns a 404.
    """
    owner = user_factory(username="owner")
    headers = {"token": AuthService.create_access_token(owner)}
    project = project_factory(user=owner)
    non_existent_user_id = 999
    
    response = client.post(
        f"/projects/{project.id}/participants",
        json={"user_id": non_existent_user_id},
        headers=headers
    )

    assert response.status_code == 404


def test_add_existing_participant(
    client: TestClient,
    user_factory: Callable[..., User],
    project_factory: Callable[..., Project]
):
    """
    Test that an attempt to add a user who is already a participant returns a 400.
    """
    owner = user_factory(username="owner")
    existing_participant = user_factory(username="existing_participant")
    headers = {"token": AuthService.create_access_token(owner)}
    project = project_factory(user=owner, participants=[existing_participant])
    
    response = client.post(
        f"/projects/{project.id}/participants",
        json={"user_id": existing_participant.id},
        headers=headers
    )
    
    assert response.status_code == 400


def test_unauthenticated_user_cannot_add_participant(
    client: TestClient,
    project_factory: Callable[..., Project],
    user_factory: Callable[..., User]
):
    """
    Test that an unauthenticated user cannot add participants to a project.
    """
    owner = user_factory(username="owner")
    participant_to_add = user_factory(username="new_participant")
    project = project_factory(user=owner)

    response = client.post(
        f"/projects/{project.id}/participants",
        json={"user_id": participant_to_add.id}
    )

    assert response.status_code == 401
