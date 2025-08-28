import pytest
from unittest.mock import Mock, patch
from services import UserService
from repositories import UserRepository
from models import User
from validators import CreateUserRequest

class TestUserService:
    """
    Unit tests for the UserService class.
    We'll mock the UserRepository and AuthService to isolate UserService logic.
    """
    mock_user_repo: Mock
    user_service: UserService
    user_data: CreateUserRequest
    hashed_password: str
    created_user: User

    def setup_method(self) -> None:

        self.mock_user_repo = Mock(spec=UserRepository)
        self.user_service = UserService(self.mock_user_repo)

        self.user_data = CreateUserRequest(
            username="testuser",
            password="securepassword123",
            password_confirm="securepassword123"
        )
        self.hashed_password = "hashed_securepassword123"
        self.created_user = User(
            id=1,
            username="testuser",
            password=self.hashed_password
        )


    @patch('services.AuthService.hash_password')
    def test_register_user_success(self, mock_hash_password: Mock) -> None:
        """
        Test that a user is successfully registered when the username is unique.
        """
        
        self.mock_user_repo.get_by_username.return_value = None  # No existing user
        mock_hash_password.return_value = self.hashed_password
        self.mock_user_repo.create.return_value = self.created_user

        registered_user: User = self.user_service.register_user(self.user_data)

        self.mock_user_repo.get_by_username.assert_called_once_with(self.user_data.username)
        mock_hash_password.assert_called_once_with(self.user_data.password)
        self.mock_user_repo.create.assert_called_once_with(self.user_data, self.hashed_password)
        assert registered_user == self.created_user
        assert registered_user.username == self.user_data.username
        assert registered_user.password == self.hashed_password

    @patch('services.AuthService.hash_password')
    def test_register_user_username_exists(self, mock_hash_password: Mock) -> None:
        """
        Test that a ValueError is raised when the username already exists.
        """

        self.mock_user_repo.get_by_username.return_value = self.created_user # User already exists

        with pytest.raises(ValueError):
            self.user_service.register_user(self.user_data)

        self.mock_user_repo.get_by_username.assert_called_once_with(self.user_data.username)
        mock_hash_password.assert_not_called() 
        self.mock_user_repo.create.assert_not_called()