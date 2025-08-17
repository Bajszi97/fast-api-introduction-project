import typing
from db import Base
from datetime import datetime
from sqlalchemy import String, TIMESTAMP, func, Text, and_
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from models.enums import Role

if typing.TYPE_CHECKING:
    from models import User, UserProject


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str|None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())

    users_assoc: Mapped[List["UserProject"]] = relationship(back_populates="project", cascade="all, delete-orphan")

    users: Mapped[List["User"]] = relationship(
        secondary="user_project",
        back_populates="projects",
        viewonly=True
    )

    admins: Mapped[List["User"]] = relationship(
        secondary="user_project",
        primaryjoin=f"and_(Project.id == UserProject.project_id, UserProject.role == '{Role.admin}')",
        secondaryjoin="UserProject.user_id == User.id",
        back_populates="own_projects",
        viewonly=True
    )

    participants: Mapped[List["User"]] = relationship(
        secondary="user_project",
        primaryjoin=f"and_(Project.id == UserProject.project_id, UserProject.role == '{Role.participant}')",
        secondaryjoin="UserProject.user_id == User.id",
        back_populates="participant_projects",
        viewonly=True
    )
