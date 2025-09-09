import os
from models import Document, Project
from sqlalchemy.orm import Session
from schemas import UploadedDocument


class DocumentRepository:
    STORAGE_PATH = "./{storage_directory}/documents/{project_id}"

    def __init__(self, db: Session, use_test_dir: bool = False) -> None:
        self.db = db
        self.storage_dir = os.getenv("TEST_STORAGE_DIR", "data-test") if use_test_dir else os.getenv("STORAGE_DIR", "data")

    def get_project_document_by_id(self, project_id: int, document_id: int) -> Document:
        return self.db.query(Document).filter(Document.project_id == project_id, Document.id == document_id).first()

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

        os.makedirs(DocumentRepository.STORAGE_PATH.format(
            storage_directory=self.storage_dir, project_id=project_id), exist_ok=True)

        with open(self.get_document_path(new_document), "wb") as buffer:
            buffer.write(file.content)

        return new_document

    def update_project_document(self, document: Document, file: UploadedDocument):
        os.remove(self.get_document_path(document))

        if file.filename is not None:
            document.filename = file.filename
        if file.content_type is not None:
            document.file_type = file.content_type

        self.db.commit()
        self.db.refresh(document)

        with open(self.get_document_path(document), "wb") as buffer:
            buffer.write(file.content)

        return document

    def delete_project_document(self, document: Document):
        try:
            os.remove(self.get_document_path(document))
        except FileNotFoundError:
            pass

        self.db.delete(document)
        self.db.commit()

    def get_document_path(self, document: Document) -> str:
        return os.path.join(self.STORAGE_PATH.format(
            storage_directory=self.storage_dir, project_id=document.project_id), f"{document.filename}")
