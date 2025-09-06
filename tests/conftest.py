import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from unittest.mock import Mock
from sqlalchemy import text
from main import app
from db import get_db, get_test_db, TEST_DB_URL, test_engine, Base
from repositories import UserRepository, ProjectRepository, DocumentRepository
from services import UserService, ProjectService, DocumentService
from validators import CreateUserRequest, CreateProjectRequest, UploadedDocument

@pytest.fixture(scope="session", autouse=True)
def apply_migrations():
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", TEST_DB_URL)

    command.upgrade(alembic_cfg, "head")
    yield
    command.downgrade(alembic_cfg, "base")

@pytest.fixture(scope="session")
def client(apply_migrations):
    app.dependency_overrides[get_db] = get_test_db
    with TestClient(app) as c:
        yield c

@pytest.fixture(autouse=True)
def truncate_tables():
    with test_engine.begin() as conn:
        conn.execute(text("SET session_replication_role = replica;"))
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())
        conn.execute(text("SET session_replication_role = DEFAULT;"))
    yield

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