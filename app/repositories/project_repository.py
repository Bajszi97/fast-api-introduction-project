from typing import List
from models import Project, UserProject, User
from models.enums import Role
from sqlalchemy.orm import Session
from validators import CreateProjectRequest


class ProjectRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, project_id: int) -> Project|None:
        return self.db.query(Project).filter(Project.id == project_id).first()

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
    
    def get_user_projects(self, user: User) -> List[Project]:
        return user.projects
    
    def update(self, project: Project, project_data: CreateProjectRequest) -> Project:
        project.name = project_data.name
        project.description = project_data.description
        self.db.commit()
        self.db.refresh(project)
        return project
    
    def delete(self, project: Project):
        self.db.delete(project)
        self.db.commit()
    
    def is_user_participant(self, project: Project, user: User) -> bool:
        return user in project.users
    
    def is_user_admin(self, project: Project, user: User) -> bool:
        return user in project.admins

