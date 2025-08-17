import typing
import os
from db import Base
from datetime import datetime
from sqlalchemy import String, TIMESTAMP, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

if typing.TYPE_CHECKING:
    from models import Project


class Document(Base):
    __tablename__ = "documents"

    STORAGE_PATH="./data/documents/{project_id}"
    DOCUMENTS_URL="/projects/{project_id}/documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    filename: Mapped[str] = mapped_column(String(128), nullable=False)
    file_type: Mapped[str] = mapped_column(String(16), nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())

    project: Mapped["Project"] = relationship(back_populates="documents")

    @property
    def path(self) -> str:
        return os.path.join(self.STORAGE_PATH.format(project_id=self.project_id), f"{self.filename}")

    @property
    def url(self) -> str:
        return f"{self.DOCUMENTS_URL.format(project_id=self.project_id)}/{self.id}"

