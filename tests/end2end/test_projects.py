from fastapi.testclient import TestClient
from typing import Callable
from sqlalchemy.orm import Session
from models import User
from factories import make_project_request
from services.auth_service import AuthService
from validators import ProjectOut


def test_user_can_create_project(client: TestClient, user_factory: Callable[..., User]):
    """
    Test that a user can create a project.
    """
    user = user_factory()
    headers = {"token": AuthService.get_token(user)}
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

def test_project_can_not_be_created_without_name(client: TestClient, user_factory: Callable[..., User]):
    """
    Test that a user can create a project.
    """
    user = user_factory()
    headers = {"token": AuthService.get_token(user)}
    project_request = {
        "name": "",
    }

    response = client.post("/projects", json=project_request, headers=headers)
    
    assert response.status_code == 422





