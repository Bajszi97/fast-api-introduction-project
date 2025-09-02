from models import User, Project
from models.enums.role import Role
from repositories import ProjectRepository, UserRepository
from validators import CreateProjectRequest
from typing import List 


class ProjectService:
    def __init__(self, project_repo: ProjectRepository, user_repo: UserRepository):
        self.project_repo = project_repo
        self.user_repo = user_repo

    def create_for_user(self, project_data: CreateProjectRequest, user: User) -> Project:
        return self.project_repo.create_for_user(project_data, user)
    
    def get_user_projects(self, user: User) -> List[Project]:
        return self.project_repo.get_user_projects(user)
    
    def get_project_for_user(self, project_id: int, user: User):
        return self.get_project_and_check_permission(project_id, user, Role.participant)
    
    def update_project_for_user(self, project_id: int, project_data: CreateProjectRequest, user: User):
        project = self.get_project_and_check_permission(project_id, user, Role.admin)
        return self.project_repo.update(project, project_data)
    
    def delete_project_for_user(self, project_id: int, user: User):
        project = self.get_project_and_check_permission(project_id, user, Role.admin)
        return self.project_repo.delete(project)

    def add_participant(self, project_id, participant_id: int, user: User):
        project = self.get_project_and_check_permission(project_id, user, Role.admin)
        
        participant = self.user_repo.get_by_id(participant_id)
        if not participant:
            raise ValueError

        if self.project_repo.is_user_participant(project, participant):
            raise RuntimeError
        
        self.project_repo.add_participant(project, participant)

    def get_project_and_check_permission(self, project_id: int, user: User, permission_level: Role):
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise LookupError("Project not found")
        if permission_level == Role.participant:
            has_permission = self.project_repo.is_user_participant(project, user)
        else:
            has_permission = self.project_repo.is_user_admin(project, user)

        if not has_permission:
            raise PermissionError
        
        return project