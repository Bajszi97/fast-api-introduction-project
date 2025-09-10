import logging
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from dependencies import get_current_user, get_project_service
from schemas import CreateProjectRequest, ProjectOut, AddParticipantRequest
from models import User
from services import ProjectService

project_router = APIRouter(prefix="/projects", tags=["Projects"])
logger = logging.getLogger("app")

@project_router.post("", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: CreateProjectRequest,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service)
):
    logger.info(f"User {current_user.id} requested to create a new project.")
    try:
        new_project = project_service.create_for_user(project, current_user)
        logger.info(f"User {current_user.id} successfully created project {new_project.id}.")
        return new_project
    except Exception as e:
        logger.error(f"User {current_user.id} failed to create project. Reason: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


@project_router.get("", response_model=List[ProjectOut])
async def list_projects(
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service)
):
    logger.info(f"User {current_user.id} requested to list their projects.")
    try:
        projects = project_service.get_user_projects(current_user)
        logger.info(f"User {current_user.id} successfully retrieved a list of {len(projects)} projects.")
        return projects
    except Exception as e:
        logger.error(f"User {current_user.id} failed to retriev projects. Reason: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


@project_router.get("/{project_id}", response_model=ProjectOut)
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service)
):  
    logger.info(f"User {current_user.id} requested to view project {project_id}.")
    try:
        project = project_service.get_project_for_user(project_id, current_user)
        logger.info(f"User {current_user.id} successfully accessed project {project_id}.")
        return project
    except LookupError:
        logger.warning(f"User {current_user.id} failed to access project {project_id}. Reason: Project not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    except PermissionError:
        logger.warning(f"User {current_user.id} failed to access project {project_id}. Reason: Access denied.")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this project")
    except Exception as e:
        logger.error(f"User {current_user.id} fafailed to access project. Reason: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


@project_router.put("/{project_id}", response_model=ProjectOut)
async def update_project(
    project_id: int,
    project_update: CreateProjectRequest,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service)
):
    logger.info(f"User {current_user.id} requested to update project {project_id}.")
    try:
        updated_project = project_service.update_project_for_user(project_id, project_update, current_user)
        logger.info(f"User {current_user.id} successfully updated project {project_id}.")
        return updated_project
    except LookupError:
        logger.warning(f"User {current_user.id} failed to update project {project_id}. Reason: Project not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    except PermissionError:
        logger.warning(f"User {current_user.id} failed to update project {project_id}. Reason: Permission denied.")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to update this project")
    except Exception as e:
        logger.error(f"User {current_user.id} failed to update project. Reason: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


@project_router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service)
):
    logger.info(f"User {current_user.id} requested to delete project {project_id}.")
    try:
        project_service.delete_project_for_user(project_id, current_user)
        logger.info(f"User {current_user.id} successfully deleted project {project_id}.")
    except LookupError:
        logger.warning(f"User {current_user.id} failed to delete project {project_id}. Reason: Project not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    except PermissionError:
        logger.warning(f"User {current_user.id} failed to delete project {project_id}. Reason: Permission denied.")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to delete this project")
    except Exception as e:
        logger.error(f"User {current_user.id} failed to delete project. Reason: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


@project_router.post("/{project_id}/participants", status_code=status.HTTP_201_CREATED)
async def add_participant(
    project_id: int,
    participant: AddParticipantRequest,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service)
):
    logger.info(f"User {current_user.id} requested to add participant {participant.user_id} to project {project_id}.")
    try:
        project_service.add_participant(project_id, participant.user_id, current_user)
        logger.info(f"User {current_user.id} successfully added participant {participant.user_id} to project {project_id}.")
        return {"message": "Participant added successfully"}
    except LookupError:
        logger.warning(f"User {current_user.id} failed to add participant. Reason: Project {project_id} not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    except PermissionError:
        logger.warning(f"User {current_user.id} failed to add participant. Reason: Permission denied.")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to add participants")
    except ValueError:
        logger.warning(f"User {current_user.id} failed to add participant. Reason: User {participant.user_id} not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except RuntimeError:
        logger.warning(f"User {current_user.id} failed to add participant. Reason: User {participant.user_id} is already a participant.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is already a participant")
    except Exception as e:
        logger.error(f"User {current_user.id} failed to add participant. Reason: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")
