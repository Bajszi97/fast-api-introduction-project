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
    
    def get_documents_of_project(self, project_id: int, user: User):
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise LookupError
        if not self.project_repo.is_user_participant(project, user):
            raise PermissionError
        
        return self.document_repo.get_documents_of_project(project)
    
    def get_project_document(self, project_id: int, document_id: int, user: User):
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise LookupError("Project not found")
        if not self.project_repo.is_user_participant(project, user):
            raise PermissionError
        
        document = self.document_repo.get_project_document_by_id(project.id, document_id) 
        if not document:
            raise LookupError("Project's document not found")
        
        return document    
    
    def update_document_for_project(self, project_id: int, document_id: int, file: UploadedDocument, user: User):
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise LookupError("Project not found")
        if not self.project_repo.is_user_participant(project, user):
            raise PermissionError
        
        document = self.document_repo.get_project_document_by_id(project.id, document_id) 
        if not document:
            raise LookupError("Project's document not found")
        
        return self.document_repo.update_project_document(document, file)
        
        