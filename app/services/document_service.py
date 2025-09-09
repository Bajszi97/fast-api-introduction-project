from models import User, Document
from models.enums.role import Role
from repositories import DocumentRepository
from services import ProjectService
from schemas import UploadedDocument


class DocumentService:
    def __init__(self, document_repo: DocumentRepository, project_service: ProjectService):
        self.document_repo = document_repo
        self.project_service = project_service

    def create_document_for_project(self, project_id: int, file: UploadedDocument, user: User):
        project = self.project_service.get_project_and_check_permission(
            project_id, user, Role.participant)

        if self.document_repo.get_project_document_by_filename(project.id, file.filename):
            raise ValueError

        return self.document_repo.create_project_document(project.id, file)

    def get_documents_of_project(self, project_id: int, user: User):
        project = self.project_service.get_project_and_check_permission(
            project_id, user, Role.participant)

        return self.document_repo.get_documents_of_project(project)

    def get_project_document(self, project_id: int, document_id: int, user: User):
        project = self.project_service.get_project_and_check_permission(
            project_id, user, Role.participant)

        document = self.document_repo.get_project_document_by_id(
            project.id, document_id)
        if not document:
            raise LookupError("Project's document not found")

        return document

    def update_document_for_project(self, project_id: int, document_id: int, file: UploadedDocument, user: User):
        project = self.project_service.get_project_and_check_permission(
            project_id, user, Role.participant)

        document = self.document_repo.get_project_document_by_id(
            project.id, document_id)
        if not document:
            raise LookupError("Project's document not found")

        document_with_this_name = self.document_repo.get_project_document_by_filename(project.id, file.filename)
        if document_with_this_name and document_with_this_name.id != document.id:
            raise ValueError

        return self.document_repo.update_project_document(document, file)

    def delete_project_document(self, project_id: int, document_id: int, user: User):
        project = self.project_service.get_project_and_check_permission(
            project_id, user, Role.participant)

        document = self.document_repo.get_project_document_by_id(
            project.id, document_id)
        if not document:
            raise LookupError("Project's document not found")

        self.document_repo.delete_project_document(document)
    
    def get_document_path(self, document: Document):
        return self.document_repo.get_document_path(document)
