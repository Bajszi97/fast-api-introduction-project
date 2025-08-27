from repositories import ProjectRepository, DocumentRepository


class DocumentService:
    def __init__(self, document_repo: DocumentRepository, project_repo: ProjectRepository):
        self.document_repo = document_repo
        self.project_repo = project_repo