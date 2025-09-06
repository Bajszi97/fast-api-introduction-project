import pytest
from fastapi.testclient import TestClient
from factories import make_register_request
from typing import Callable
from models import User
from sqlalchemy.orm import Session

def test_register_and_login(client: TestClient):
    """
    Test that a user can register and login with those credentials.
    """

    # --- 1. Register a new user ---
    register_data = make_register_request()

    response = client.post("/auth", json=register_data.model_dump())
    
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["username"] == register_data.username

    # --- 2. Login with the same credentials ---
    login_data = {
        "username": register_data.username,
        "password": register_data.password
    }

    response = client.post("/login", json=login_data)
    
    assert response.status_code == 200
    token_data = response.json()
    assert "token" in token_data
    assert token_data["token"] == "login-token-testuser"

def test_username_already_taken(client: TestClient, test_db: Session, user_factory: Callable[..., User]):
    """
    Test that a user can not register if the username is already taken.
    """

    existing_user = user_factory()
    register_data = make_register_request(username=existing_user.username)

    response = client.post("/auth", json=register_data.model_dump())
    
    assert response.status_code == 400
    count = test_db.query(User).filter(User.username == existing_user.username).count()
    assert count == 1

def test_user_can_not_login_with_wrong_password(client: TestClient, user_factory: Callable[..., User]):
    """
    Test that a user can not login with a wrong password.
    """

    existing_user = user_factory()
    login_data = {
        "username": existing_user.username,
        "password": "wrongpassword"
    }

    response = client.post("/login", json=login_data)
    
    assert response.status_code == 401
    token_data = response.json()
    assert "token" not in token_data

def test_unregistered_user_can_not_login(client: TestClient):
    """
    Test that an unregistered user can not login.
    """
    
    login_data = {
        "username": "notexistinguser",
        "password": "notexistingpw"
    }

    response = client.post("/login", json=login_data)
    
    assert response.status_code == 401
    token_data = response.json()
    assert "token" not in token_data