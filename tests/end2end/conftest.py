import os
import shutil
import pytest
from typing import List
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import text
from dependencies import get_document_repository, get_test_document_repository
from main import app
from db import get_db, get_test_db, TEST_DB_URL, Base
from models import User, Project
from factories import create_document, create_project, create_user


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
    app.dependency_overrides[get_document_repository] = get_test_document_repository
    with TestClient(app) as c:
        yield c

@pytest.fixture(autouse=True)
def truncate_tables(test_db):
    yield
    test_engine = test_db.get_bind()
    with test_engine.begin() as conn:
        conn.execute(text("SET session_replication_role = replica;"))
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())
        conn.execute(text("SET session_replication_role = DEFAULT;"))

@pytest.fixture(autouse=True)
def delete_files():
    yield

    test_dir = os.getenv("TEST_STORAGE_DIR", "data-test")
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)

@pytest.fixture
def test_db():
    yield from get_test_db()

@pytest.fixture
def user_factory(test_db):   
    def _user_factory(username: str = "testuser", password: str = "strongtestpassword"):
        return create_user(test_db, username=username, password=password)
    return _user_factory

@pytest.fixture
def project_factory(test_db):   
    def _project_factory(user: User, name: str = "testproject", description: str = "Describing the test project", participants: List[User] = []):
        return create_project(test_db, user=user, name=name, description=description, participants=participants)
    return _project_factory

@pytest.fixture
def document_factory(test_db):   
    def _document_factory(    
        project: Project,
        filename: str = "test_file.txt",
        content: str = "Text file content.",
        file_type: str = "text/plain"
    ):
        return create_document(test_db, project=project, filename=filename, content=content, file_type=file_type)
    return _document_factory