from sqlalchemy.orm import Session


class DocumentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db