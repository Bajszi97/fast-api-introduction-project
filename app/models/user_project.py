import typing
from db import Base
from datetime import datetime
from sqlalchemy import func, ForeignKey, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.enums import Role

if typing.TYPE_CHECKING:
    from models import User, Project


class UserProject(Base):
    __tablename__ = "user_project"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), primary_key=True)
    role: Mapped[Role] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="projects_assoc")
    project: Mapped["Project"] = relationship(back_populates="users_assoc")

