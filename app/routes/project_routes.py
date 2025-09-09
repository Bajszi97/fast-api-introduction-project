from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from dependencies import get_current_user, get_project_service
from schemas import CreateProjectRequest, ProjectOut, AddParticipantRequest
from models import User
from services import ProjectService

project_router = APIRouter(prefix="/projects", tags=["Projects"])

@project_router.post("", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: CreateProjectRequest,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service)
):
    return project_service.create_for_user(project, current_user)


@project_router.get("", response_model=List[ProjectOut])
async def list_projects(
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service)
):
    return project_service.get_user_projects(current_user)


@project_router.get("/{project_id}", response_model=ProjectOut)
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service)
):  
    try:
        return project_service.get_project_for_user(project_id, current_user)
    except LookupError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this project")


@project_router.put("/{project_id}", response_model=ProjectOut)
async def update_project(
    project_id: int,
    project_update: CreateProjectRequest,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service)
):
    try:
        return project_service.update_project_for_user(project_id, project_update, current_user)
    except LookupError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to update this project")



@project_router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service)
):
    try:
        return project_service.delete_project_for_user(project_id, current_user)
    except LookupError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to delete this project")


@project_router.post("/{project_id}/participants", status_code=status.HTTP_201_CREATED)
async def add_participant(
    project_id: int,
    participant: AddParticipantRequest,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service)
):
    try:
        project_service.add_participant(project_id, participant.user_id, current_user)
    except LookupError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to add participants")
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except RuntimeError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is already a participant")

    return {"message": "Participant added successfully"}
