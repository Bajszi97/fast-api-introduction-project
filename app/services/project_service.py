from models import User, Project
from repositories import ProjectRepository
from validators import CreateProjectRequest


class ProjectService:
    def __init__(self, repo: ProjectRepository):
        self.repo = repo

    def create_for_user(self, project_data: CreateProjectRequest, user: User) -> Project:
        return self.repo.create_for_user(project_data, user)
