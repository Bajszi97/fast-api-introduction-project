import pytest
from unittest.mock import Mock
from models.enums.role import Role
from services import ProjectService
from factories import make_project, make_user
from validators import CreateProjectRequest


class TestProjectService:
    """
    Unit tests for the ProjectService class.
    """

    def test_create_project_for_user(
        self,
        project_repo_mock: Mock,
        project_service: ProjectService,
        project_data: CreateProjectRequest
    ) -> None:         
        """
        Test that creating project is delegated to the repository.
        """
        user = make_user()
        project = make_project()
        project_repo_mock.create_for_user.return_value = project

        result = project_service.create_for_user(project_data, user)

        project_repo_mock.create_for_user.assert_called_once_with(project_data, user)
        assert result is project

    def test_get_user_project(
        self,
        project_repo_mock: Mock,
        project_service: ProjectService
    ) -> None:
        """
        Testing that fetching user projects is delegated to the repository.
        """
        user = make_user()
        project = make_project()
        project2 = make_project(id=2)
        project_repo_mock.get_user_projects.return_value = [project, project2]

        result = project_service.get_user_projects(user)

        project_repo_mock.get_user_projects.assert_called_once_with(user)
        assert result == [project, project2]

    def test_get_project_for_user_success(
        self,
        project_repo_mock: Mock,
        project_service: ProjectService,
    ) -> None:
        """
        Testing that it fetches the requested project
        """
        user = make_user()
        project = make_project()
        project_repo_mock.get_by_id.return_value = project
        project_repo_mock.is_user_participant.return_value = True

        result = project_service.get_project_for_user(project.id, user)

        project_repo_mock.get_by_id.assert_called_once_with(project.id)
        project_repo_mock.is_user_participant.assert_called_once_with(project, user)
        assert result is project

    def test_get_project_for_user_not_found(
        self,
        project_service: ProjectService,
        project_repo_mock: Mock
    ) -> None:
        """
        Testing that it raises an Error if project is not found
        """
        user = make_user()
        project = make_project()
        project_repo_mock.get_by_id.return_value = None

        with pytest.raises(LookupError):
            project_service.get_project_for_user(project.id, user)

        project_repo_mock.get_user_projects.assert_not_called()

    def test_get_project_for_user_permission_denied(
        self,
        project_service: ProjectService,
        project_repo_mock: Mock
    ) -> None:
        """
        Testing that it raises an Error if user doesn't have permission
        """
        user = make_user()
        project = make_project()
        project_repo_mock.get_by_id.return_value = project
        project_repo_mock.is_user_participant.return_value = False

        with pytest.raises(PermissionError):
            project_service.get_project_for_user(project.id, user)

        project_repo_mock.get_user_projects.assert_not_called()

    def test_update_project_for_user_success(
        self,
        project_repo_mock: Mock,
        project_service: ProjectService,
        project_data: CreateProjectRequest
    ) -> None:
        """
        Testing that it updates the requested project
        """
        user = make_user()
        old_project = make_project(name="Old Project")
        new_project = make_project(id=old_project.id, name=project_data.name, description=project_data.description)
        project_repo_mock.get_by_id.return_value = old_project
        project_repo_mock.is_user_admin.return_value = True
        project_repo_mock.update.return_value = new_project

        result = project_service.update_project_for_user(old_project.id, project_data, user)

        project_repo_mock.get_by_id.assert_called_once_with(old_project.id)
        project_repo_mock.is_user_admin.assert_called_once_with(old_project, user)
        project_repo_mock.update.assert_called_once_with(old_project, project_data)
        assert result is new_project

    def test_update_project_for_user_not_found(
        self,
        project_repo_mock: Mock,
        project_service: ProjectService,
        project_data: CreateProjectRequest
    ) -> None:
        """
        Testing that it raises an Error if project is not found
        """
        user = make_user()
        old_project = make_project(name="Old Project")
        project_repo_mock.get_by_id.return_value = None


        with pytest.raises(LookupError):
            project_service.update_project_for_user(old_project.id, project_data, user)

        project_repo_mock.update.assert_not_called()

    def test_update_project_for_user_permission_denied(
        self,
        project_repo_mock: Mock,
        project_service: ProjectService,
        project_data: CreateProjectRequest
    ) -> None:
        """
        Testing that it raises an Error if user doesn't have permission
        """
        user = make_user()
        old_project = make_project(name="Old Project")
        project_repo_mock.get_by_id.return_value = old_project
        project_repo_mock.is_user_admin.return_value = False

        with pytest.raises(PermissionError):
            project_service.update_project_for_user(old_project.id, project_data, user)

        project_repo_mock.update.assert_not_called()

    def test_delete_project_for_user_success(
        self,
        project_repo_mock: Mock,
        project_service: ProjectService,
    ) -> None:
        """
        Testing that it removes the requested project
        """
        user = make_user()
        project = make_project()
        project_repo_mock.get_by_id.return_value = project
        project_repo_mock.is_user_admin.return_value = True
        project_repo_mock.delete.return_value = None

        result = project_service.delete_project_for_user(project.id, user)

        project_repo_mock.get_by_id.assert_called_once_with(project.id)
        project_repo_mock.is_user_admin.assert_called_once_with(project, user)
        project_repo_mock.delete.assert_called_once_with(project)
        assert result is None

    def test_delete_project_for_user_not_found(
        self,
        project_repo_mock: Mock,
        project_service: ProjectService,
    ) -> None:
        """
        Testing that it raises an Error if project is not found
        """
        user = make_user()
        project = make_project()
        project_repo_mock.get_by_id.return_value = None

        with pytest.raises(LookupError):
            project_service.delete_project_for_user(project.id, user)

        project_repo_mock.delete.assert_not_called()

    def test_delete_project_for_user_permission_denied(
        self,
        project_repo_mock: Mock,
        project_service: ProjectService,
    ) -> None:
        """
        Testing that it raises an Error if user doesn't have permission
        """
        user = make_user()
        project = make_project()
        project_repo_mock.get_by_id.return_value = project
        project_repo_mock.is_user_admin.return_value = False

        with pytest.raises(PermissionError):
            project_service.delete_project_for_user(project.id, user)

        project_repo_mock.delete.assert_not_called()


    def test_add_participant_success(
        self,
        project_repo_mock: Mock,
        user_repo_mock: Mock,
        project_service: ProjectService,
    ) -> None:
        """
        Testing that it adds participants
        """
        user = make_user()
        participant = make_user(id=2, username="Would be Participant")
        project = make_project()
        project_repo_mock.get_by_id.return_value = project
        project_repo_mock.is_user_admin.return_value = True
        user_repo_mock.get_by_id.return_value = participant
        project_repo_mock.is_user_participant.return_value = False

        result = project_service.add_participant(project.id, participant.id, user)

        project_repo_mock.get_by_id.assert_called_once_with(project.id)
        project_repo_mock.is_user_admin.assert_called_once_with(project, user)
        user_repo_mock.get_by_id.assert_called_once_with(participant.id)
        project_repo_mock.is_user_participant.assert_called_once_with(project, participant)
        project_repo_mock.add_participant.assert_called_once_with(project, participant)
        assert result is None

    def test_add_participant_not_found(
        self,
        project_repo_mock: Mock,
        project_service: ProjectService,
    ) -> None:
        """
        Testing that it raises an Error if project is not found
        """
        user = make_user()
        participant = make_user(id=2, username="Would be Participant")
        project = make_project()
        project_repo_mock.get_by_id.return_value = None 

        with pytest.raises(LookupError):
            project_service.add_participant(project.id, participant.id, user)

        project_repo_mock.add_participant.assert_not_called()

    def test_add_participant_permission_denied(
        self,
        project_repo_mock: Mock,
        project_service: ProjectService,
    ) -> None:
        """
        Testing that it raises an Error if user doesn't have permission
        """
        user = make_user()
        participant = make_user(id=2, username="Would be Participant")
        project = make_project()
        project_repo_mock.get_by_id.return_value = project
        project_repo_mock.is_user_admin.return_value = False

        with pytest.raises(PermissionError):
            project_service.add_participant(project.id, participant.id, user)

        project_repo_mock.add_participant.assert_not_called()

    def test_add_participant_user_not_found(
        self,
        project_repo_mock: Mock,
        user_repo_mock: Mock,
        project_service: ProjectService,
    ) -> None:
        """
        Testing that it raises an Error if participant user not found
        """
        user = make_user()
        participant = make_user(id=2, username="Would be Participant")
        project = make_project()
        project_repo_mock.get_by_id.return_value = project
        project_repo_mock.is_user_admin.return_value = True
        user_repo_mock.get_by_id.return_value = None

        with pytest.raises(ValueError):
            project_service.add_participant(project.id, participant.id, user)

        project_repo_mock.add_participant.assert_not_called()

    def test_add_participant_already_participant(
        self,
        project_repo_mock: Mock,
        user_repo_mock: Mock,
        project_service: ProjectService,
    ) -> None:
        """
        Testing that it raises an Error if participant user not found
        """
        user = make_user()
        participant = make_user(id=2, username="Would be Participant")
        project = make_project()
        project_repo_mock.get_by_id.return_value = project
        project_repo_mock.is_user_admin.return_value = True
        user_repo_mock.get_by_id.return_value = participant
        project_repo_mock.is_user_participant.return_value = True

        with pytest.raises(RuntimeError):
            project_service.add_participant(project.id, participant.id, user)

        project_repo_mock.add_participant.assert_not_called()

    def test_get_project_and_check_permission_participant_success(
        self,
        project_repo_mock: Mock,
        project_service: ProjectService
    ) -> None:
        """
        Test that a project is returned when the user has participant permission.
        """
        user = make_user()
        project = make_project()
        project_repo_mock.get_by_id.return_value = project
        project_repo_mock.is_user_participant.return_value = True

        result = project_service.get_project_and_check_permission(project.id, user, Role.participant)

        project_repo_mock.get_by_id.assert_called_once_with(project.id)
        project_repo_mock.is_user_participant.assert_called_once_with(project, user)
        assert result is project

    def test_get_project_and_check_permission_admin_success(
        self,
        project_repo_mock: Mock,
        project_service: ProjectService
    ) -> None:
        """
        Test that a project is returned when the user has admin permission.
        """
        user = make_user()
        project = make_project()
        project_repo_mock.get_by_id.return_value = project
        project_repo_mock.is_user_admin.return_value = True

        result = project_service.get_project_and_check_permission(project.id, user, Role.admin)

        project_repo_mock.get_by_id.assert_called_once_with(project.id)
        project_repo_mock.is_user_admin.assert_called_once_with(project, user)
        project_repo_mock.is_user_participant.assert_not_called()
        assert result is project

    def test_get_project_and_check_permission_project_not_found(
        self,
        project_repo_mock: Mock,
        project_service: ProjectService
    ) -> None:
        """
        Test that LookupError is raised if the project is not found.
        """
        user = make_user()
        project = make_project()
        project_repo_mock.get_by_id.return_value = None

        with pytest.raises(LookupError):
            project_service.get_project_and_check_permission(project.id, user, Role.participant)

        project_repo_mock.is_user_participant.assert_not_called()

    def test_get_project_and_check_permission_participant_denied(
        self,
        project_repo_mock: Mock,
        project_service: ProjectService
    ) -> None:
        """
        Test that PermissionError is raised for a participant when access is denied.
        """
        user = make_user()
        project = make_project()
        project_repo_mock.get_by_id.return_value = project
        project_repo_mock.is_user_participant.return_value = False

        with pytest.raises(PermissionError):
            project_service.get_project_and_check_permission(project.id, user, Role.participant)

    def test_get_project_and_check_permission_admin_denied(
        self,
        project_repo_mock: Mock,
        project_service: ProjectService
    ) -> None:
        """
        Test that PermissionError is raised for an admin when access is denied.
        """
        user = make_user()
        project = make_project()
        project_repo_mock.get_by_id.return_value = project
        project_repo_mock.is_user_admin.return_value = False

        with pytest.raises(PermissionError):
            project_service.get_project_and_check_permission(project.id, user, Role.admin)


    
