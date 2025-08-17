import typing
from db import Base
from datetime import datetime
from sqlalchemy import String, TIMESTAMP, func, and_
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from models.enums import Role

if typing.TYPE_CHECKING:
    from models import Project, UserProject


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(256), nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    projects: Mapped[List["Project"]] = relationship(back_populates="users")

    projects_assoc: Mapped[list["UserProject"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    projects: Mapped[list["Project"]] = relationship(
        secondary="user_project",
        back_populates="users",
        viewonly=True
    )

    own_projects: Mapped[list["Project"]] = relationship(
        secondary="user_project",
        primaryjoin=f"and_(User.id == UserProject.user_id, UserProject.role == '{Role.admin}')",
        secondaryjoin="UserProject.project_id == Project.id",
        viewonly=True,
        back_populates="admins"
    )

    participant_projects: Mapped[list["Project"]] = relationship(
        secondary="user_project",
        primaryjoin=f"and_(User.id == UserProject.user_id, UserProject.role == '{Role.participant}')",
        secondaryjoin="UserProject.project_id == Project.id",
        viewonly=True,
        back_populates="participants"
    )