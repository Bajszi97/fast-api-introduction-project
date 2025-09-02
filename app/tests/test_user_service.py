import pytest
from unittest.mock import Mock, patch
from services import UserService
from models import User
from tests.factories import make_user
from validators import CreateUserRequest

class TestUserService:
    """
    Unit tests for the UserService class.
    """

    @patch('services.AuthService.hash_password')
    def test_register_user_success(
        self,
        mock_hash_password: Mock,
        user_repo_mock: Mock,
        user_service: UserService,
        user_data: CreateUserRequest
    ) -> None:
        """
        Test that a user is successfully registered when the username is unique.
        """
        
        user_repo_mock.get_by_username.return_value = None  # No existing user
        hashed_password = "hashed_securepassword123"
        mock_hash_password.return_value = hashed_password
        created_user = make_user(username=user_data.username, password=hashed_password)
        user_repo_mock.create.return_value = created_user

        registered_user: User = user_service.register_user(user_data)

        user_repo_mock.get_by_username.assert_called_once_with(user_data.username)
        mock_hash_password.assert_called_once_with(user_data.password)
        user_repo_mock.create.assert_called_once_with(user_data, hashed_password)
        assert registered_user is created_user

    @patch('services.AuthService.hash_password')
    def test_register_user_username_exists(
        self,
        mock_hash_password: Mock,
        user_repo_mock: Mock,
        user_service: UserService,
        user_data: CreateUserRequest
    ) -> None:
        """
        Test that a ValueError is raised when the username already exists.
        """

        existing_user = make_user(username=user_data.username)
        user_repo_mock.get_by_username.return_value = existing_user # User already exists

        with pytest.raises(ValueError):
            user_service.register_user(user_data)

        user_repo_mock.get_by_username.assert_called_once_with(user_data.username)
        mock_hash_password.assert_not_called() 
        user_repo_mock.create.assert_not_called()