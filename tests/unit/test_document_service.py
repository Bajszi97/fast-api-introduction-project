import pytest
from unittest.mock import Mock
from models.enums.role import Role
from services import DocumentService
from factories import make_document, make_project, make_user
from validators import UploadedDocument


class TestDocumentService:
    """
    Unit tests for the DocumentService class.
    """

    def test_create_document_for_project(
        self,
        project_service_mock: Mock,
        document_repo_mock: Mock,
        document_service: DocumentService,
        document_data: UploadedDocument
    ) -> None:
        """
        Test that a document is added to a project
        """
        user = make_user()
        project = make_project()
        document = make_document()
        project_service_mock.get_project_and_check_permission.return_value = project
        document_repo_mock.get_project_document_by_filename.return_value = None
        document_repo_mock.create_project_document.return_value = document

        result = document_service.create_document_for_project(project.id, document_data, user)

        project_service_mock.get_project_and_check_permission.assert_called_once_with(project.id, user, Role.participant)
        document_repo_mock.get_project_document_by_filename.assert_called_once_with(project.id, document_data.filename)
        document_repo_mock.create_project_document.assert_called_once_with(project.id, document_data)
        assert result is document
    
    def test_create_document_for_project_not_found(
        self,
        project_service_mock: Mock,
        document_repo_mock: Mock,
        document_service: DocumentService,
        document_data: UploadedDocument
    ) -> None:
        """"
        Test that it raises an Error if project is not found
        """
        user = make_user()
        project = make_project()
        project_service_mock.get_project_and_check_permission.side_effect = LookupError

        with pytest.raises(LookupError):
            document_service.create_document_for_project(project.id, document_data, user)

        document_repo_mock.create_project_document.assert_not_called()
    
    def test_create_document_for_project_permission_denied(
        self,
        project_service_mock: Mock,
        document_repo_mock: Mock,
        document_service: DocumentService,
        document_data: UploadedDocument
    ) -> None:
        """
        Test that an Error is raised when the user doesn't has permission to add doucment
        """
        user = make_user()
        project = make_project()
        project_service_mock.get_project_and_check_permission.side_effect = PermissionError

        with pytest.raises(PermissionError):
            document_service.create_document_for_project(project.id, document_data, user)

        document_repo_mock.create_project_document.assert_not_called()
    
    def test_create_document_for_project_duplicate_filename(
        self,
        project_service_mock: Mock,
        document_repo_mock: Mock,
        document_service: DocumentService,
        document_data: UploadedDocument
    ) -> None:
        """
        Test that an Error is raised when the file name is already exists
        """
        user = make_user()
        project = make_project()
        document = make_document()
        project_service_mock.get_project_and_check_permission.return_value = project
        document_repo_mock.get_project_document_by_filename.return_value = document

        with pytest.raises(ValueError):
            document_service.create_document_for_project(project.id, document_data, user)

        document_repo_mock.create_project_document.assert_not_called()
    
    def test_get_documents_of_project(
        self,
        project_service_mock: Mock,
        document_repo_mock: Mock,
        document_service: DocumentService
    ) -> None:
        """
        Test that all documents of a project are returned.
        """
        user = make_user()
        project = make_project()
        documents = [make_document() for _ in range(3)]
        project_service_mock.get_project_and_check_permission.return_value = project
        document_repo_mock.get_documents_of_project.return_value = documents

        result = document_service.get_documents_of_project(project.id, user)

        project_service_mock.get_project_and_check_permission.assert_called_once_with(project.id, user, Role.participant)
        document_repo_mock.get_documents_of_project.assert_called_once_with(project)
        assert result == documents

    def test_get_documents_of_project_not_found(
        self,
        project_service_mock: Mock,
        document_repo_mock: Mock,
        document_service: DocumentService
    ) -> None:
        """
        Test that it raises an Error if project is not found when getting documents.
        """
        user = make_user()
        project = make_project()
        project_service_mock.get_project_and_check_permission.side_effect = LookupError

        with pytest.raises(LookupError):
            document_service.get_documents_of_project(project.id, user)

        document_repo_mock.get_documents_of_project.assert_not_called()

    def test_get_documents_of_project_permission_denied(
        self,
        project_service_mock: Mock,
        document_repo_mock: Mock,
        document_service: DocumentService
    ) -> None:
        """
        Test that it raises a PermissionError if the user doesn't have access to the project.
        """
        user = make_user()
        project = make_project()
        project_service_mock.get_project_and_check_permission.side_effect = PermissionError

        with pytest.raises(PermissionError):
            document_service.get_documents_of_project(project.id, user)

        document_repo_mock.get_documents_of_project.assert_not_called()

    def test_get_project_document(
        self,
        project_service_mock: Mock,
        document_repo_mock: Mock,
        document_service: DocumentService
    ) -> None:
        """
        Test that a specific document can be retrieved.
        """
        user = make_user()
        project = make_project()
        document = make_document()
        project_service_mock.get_project_and_check_permission.return_value = project
        document_repo_mock.get_project_document_by_id.return_value = document

        result = document_service.get_project_document(project.id, document.id, user)

        project_service_mock.get_project_and_check_permission.assert_called_once_with(project.id, user, Role.participant)
        document_repo_mock.get_project_document_by_id.assert_called_once_with(project.id, document.id)
        assert result is document

    def test_get_project_document_not_found(
        self,
        project_service_mock: Mock,
        document_repo_mock: Mock,
        document_service: DocumentService
    ) -> None:
        """
        Test that it raises an Error if the document is not found.
        """
        user = make_user()
        project = make_project()
        project_service_mock.get_project_and_check_permission.return_value = project
        document_repo_mock.get_project_document_by_id.return_value = None

        with pytest.raises(LookupError):
            document_service.get_project_document(project.id, 123, user)

        document_repo_mock.get_project_document_by_id.assert_called_once()

    def test_get_project_document_permission_denied(
        self,
        project_service_mock: Mock,
        document_repo_mock: Mock,
        document_service: DocumentService
    ) -> None:
        """
        Test that a PermissionError is raised if the user doesn't have access.
        """
        user = make_user()
        project = make_project()
        project_service_mock.get_project_and_check_permission.side_effect = PermissionError

        with pytest.raises(PermissionError):
            document_service.get_project_document(project.id, 123, user)

        document_repo_mock.get_project_document_by_id.assert_not_called()

    def test_update_document_for_project(
        self,
        project_service_mock: Mock,
        document_repo_mock: Mock,
        document_service: DocumentService,
        document_data: UploadedDocument
    ) -> None:
        """
        Test that a document can be updated for a project.
        """
        user = make_user()
        project = make_project()
        document = make_document()
        project_service_mock.get_project_and_check_permission.return_value = project
        document_repo_mock.get_project_document_by_id.return_value = document
        document_repo_mock.get_project_document_by_filename.return_value = document
        document_repo_mock.update_project_document.return_value = document

        result = document_service.update_document_for_project(project.id, document.id, document_data, user)

        project_service_mock.get_project_and_check_permission.assert_called_once_with(project.id, user, Role.participant)
        document_repo_mock.get_project_document_by_id.assert_called_once_with(project.id, document.id)
        document_repo_mock.get_project_document_by_filename.assert_called_once_with(project.id, document.filename)
        document_repo_mock.update_project_document.assert_called_once_with(document, document_data)
        assert result is document

    def test_update_document_for_project_project_not_found(
        self,
        project_service_mock: Mock,
        document_repo_mock: Mock,
        document_service: DocumentService,
        document_data: UploadedDocument
    ) -> None:
        """
        Test that it raises an Error if the project is not found when updating.
        """
        user = make_user()
        project = make_project()
        document = make_document()
        project_service_mock.get_project_and_check_permission.side_effect = LookupError

        with pytest.raises(LookupError):
            document_service.update_document_for_project(project.id, document.id, document_data, user)

        document_repo_mock.update_project_document.assert_not_called()
    
    def test_update_document_for_project_permission_denied(
        self,
        project_service_mock: Mock,
        document_repo_mock: Mock,
        document_service: DocumentService,
        document_data: UploadedDocument
    ) -> None:
        """
        Test that it raises a PermissionError when the user doesn't have permission to update.
        """
        user = make_user()
        project = make_project()
        document = make_document()
        project_service_mock.get_project_and_check_permission.side_effect = PermissionError

        with pytest.raises(PermissionError):
            document_service.update_document_for_project(project.id, document.id, document_data, user)

        document_repo_mock.update_project_document.assert_not_called()

    def test_update_document_for_project_document_not_found(
        self,
        project_service_mock: Mock,
        document_repo_mock: Mock,
        document_service: DocumentService,
        document_data: UploadedDocument
    ) -> None:
        """
        Test that it raises an Error if the document to be updated is not found.
        """
        user = make_user()
        project = make_project()
        document = make_document()
        project_service_mock.get_project_and_check_permission.return_value = project
        document_repo_mock.get_project_document_by_id.return_value = None

        with pytest.raises(LookupError):
            document_service.update_document_for_project(project.id, document.id, document_data, user)

        document_repo_mock.update_project_document.assert_not_called()

    def test_delete_project_document(
        self,
        project_service_mock: Mock,
        document_repo_mock: Mock,
        document_service: DocumentService
    ) -> None:
        """
        Test that a document can be deleted from a project.
        """
        user = make_user()
        project = make_project()
        document = make_document()
        project_service_mock.get_project_and_check_permission.return_value = project
        document_repo_mock.get_project_document_by_id.return_value = document
        document_repo_mock.delete_project_document.return_value = None

        result = document_service.delete_project_document(project.id, document.id, user)

        project_service_mock.get_project_and_check_permission.assert_called_once_with(project.id, user, Role.participant)
        document_repo_mock.get_project_document_by_id.assert_called_once_with(project.id, document.id)
        document_repo_mock.delete_project_document.assert_called_once_with(document)
        assert result is None
    
    def test_delete_project_document_project_not_found(
        self,
        project_service_mock: Mock,
        document_repo_mock: Mock,
        document_service: DocumentService
    ) -> None:
        """
        Test that it raises an Error if the project is not found when deleting a document.
        """
        user = make_user()
        project = make_project()
        document = make_document()
        project_service_mock.get_project_and_check_permission.side_effect = LookupError

        with pytest.raises(LookupError):
            document_service.delete_project_document(project.id, document.id, user)

        document_repo_mock.delete_project_document.assert_not_called()

    def test_delete_project_document_permission_denied(
        self,
        project_service_mock: Mock,
        document_repo_mock: Mock,
        document_service: DocumentService
    ) -> None:
        """
        Test that it raises a PermissionError when the user doesn't have permission to delete a document.
        """
        user = make_user()
        project = make_project()
        document = make_document()
        project_service_mock.get_project_and_check_permission.side_effect = PermissionError

        with pytest.raises(PermissionError):
            document_service.delete_project_document(project.id, document.id, user)

        document_repo_mock.delete_project_document.assert_not_called()
    
    def test_delete_project_document_document_not_found(
        self,
        project_service_mock: Mock,
        document_repo_mock: Mock,
        document_service: DocumentService
    ) -> None:
        """
        Test that it raises an Error if the document to be deleted is not found.
        """
        user = make_user()
        project = make_project()
        document = make_document()
        project_service_mock.get_project_and_check_permission.return_value = project
        document_repo_mock.get_project_document_by_id.return_value = None

        with pytest.raises(LookupError):
            document_service.delete_project_document(project.id, document.id, user)

        document_repo_mock.delete_project_document.assert_not_called()

