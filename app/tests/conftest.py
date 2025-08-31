import pytest
from unittest.mock import Mock
from repositories import UserRepository
from services import UserService
from validators import CreateUserRequest

@pytest.fixture
def user_repo_mock():
    """Fixture for a mocked UserRepository."""
    return Mock(spec=UserRepository)

@pytest.fixture
def user_service(user_repo_mock):
    """Fixture for the UserService."""
    return UserService(user_repo_mock)

@pytest.fixture
def user_data():
    """Fixture for the CreateUserRequest data."""
    return CreateUserRequest(
        username="testuser",
        password="securepassword123",
        password_confirm="securepassword123"
    )