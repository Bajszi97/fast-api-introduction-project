from models import User
from repositories import ProjectRepository, DocumentRepository
from validators import UploadedDocument


class DocumentService:
    def __init__(self, document_repo: DocumentRepository, project_repo: ProjectRepository):
        self.document_repo = document_repo
        self.project_repo = project_repo

    def create_document_for_project(self, project_id: int, file: UploadedDocument, user: User):
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise LookupError
        if not self.project_repo.is_user_participant(project, user):
            raise PermissionError
        
        if self.document_repo.get_project_document_by_filename(project.id, file.filename):
            raise ValueError
        
        return self.document_repo.create_project_document(project.id, file)

        