import pytest
from unittest.mock import Mock
from repositories import UserRepository, ProjectRepository, DocumentRepository
from services import UserService, ProjectService, DocumentService
from validators import CreateUserRequest, CreateProjectRequest, UploadedDocument

@pytest.fixture
def user_repo_mock():
    """Fixture for a mocked UserRepository."""
    return Mock(spec=UserRepository)

@pytest.fixture
def user_service(user_repo_mock):
    """Fixture for the UserService."""
    return UserService(user_repo_mock)

@pytest.fixture
def project_repo_mock():
    """Fixture for a mocked ProjectRepository."""
    return Mock(spec=ProjectRepository)

@pytest.fixture
def project_service(user_repo_mock, project_repo_mock):
    """Fixture for the ProjectService."""
    return ProjectService(project_repo_mock, user_repo_mock)

@pytest.fixture
def document_repo_mock():
    """Fixture for a mocked DocumentRepository."""
    return Mock(spec=DocumentRepository)

@pytest.fixture
def project_service_mock():
    """Fixture for a mocked ProjectService."""
    return Mock(spec=ProjectService)

@pytest.fixture
def document_service(project_service_mock, document_repo_mock):
    """Fixture for the DocumentService."""
    return DocumentService(document_repo_mock, project_service_mock)

@pytest.fixture
def user_data():
    """Fixture for the CreateUserRequest data."""
    return CreateUserRequest(
        username="testuser",
        password="securepassword123",
        password_confirm="securepassword123"
    )

@pytest.fixture
def project_data():
    """Fixture for the CreateProjectRequest data."""
    return CreateProjectRequest(
        name="Test project",
        description="Describing my test project"
    )

@pytest.fixture
def document_data():
    return UploadedDocument(
        filename="test.txt",
        content_type="text/plain",
        content=b"Test text in test.txt file"
    )