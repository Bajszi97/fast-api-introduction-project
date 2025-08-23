from models import Project, UserProject, User
from models.enums import Role
from sqlalchemy.orm import Session
from validators import CreateProjectRequest


class ProjectRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_for_user(self, project_data: CreateProjectRequest, user: User):
        new_project = Project(
            name = project_data.name,
            description = project_data.description,
        )
        self.db.add(new_project)
        self.db.flush()

        # associate with admin
        admin_assoc = UserProject(
            user_id=user.id,
            project_id=new_project.id,
            role=Role.admin
        )

        self.db.add(admin_assoc)
        self.db.commit()

        return new_project

