import os
from models import Document, Project
from sqlalchemy.orm import Session
from validators import UploadedDocument


class DocumentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_project_document_by_filename(self, project_id: int, filename):
        return self.db.query(Document).filter(Document.project_id == project_id, Document.filename == filename).first()
    
    def get_documents_of_project(self, project: Project):
        return project.documents
    
    def create_project_document(self, project_id: int, file: UploadedDocument):
        new_document = Document(
            project_id=project_id,
            filename=file.filename,
            file_type=file.content_type 
        )

        self.db.add(new_document)
        self.db.commit()
        self.db.refresh(new_document)

        os.makedirs(Document.STORAGE_PATH.format(project_id=project_id), exist_ok=True)
        
        with open(new_document.path, "wb") as buffer:
            buffer.write(file.content)

        return new_document
