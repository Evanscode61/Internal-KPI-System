from organization.models import Department
from services.utils.response_provider import ResponseProvider
from utils.common import get_clean_request_data
from services.services import DepartmentService, TeamService


class DepartmentServiceHandler:
    """
        Handles CRUD operations for Department objects, providing
        responses via ResponseProvider and serialization for API output.
        """

    @classmethod
    def create_department(cls, request) -> ResponseProvider:
        """
               Create a new department from request data.
               Args:
                   request: Django request object containing department data.
               Returns:
                   ResponseProvider: Success response with the created department.
               """
        data = get_clean_request_data(
            request,
            required_fields={'name'}
        )

        name = data.get('name')

        department = DepartmentService().create_department(
            name,
            description=data.get('description', ''),
            triggered_by=request.user,
            request=request
        )

        return ResponseProvider.created(
            message=f"{department.name} department created successfully",
            data=cls._serialize(department)
        )

    @classmethod
    def get_department(cls, dept_uuid: str) -> ResponseProvider:
        """
             Retrieve a single department by UUID.
             Args:
                 dept_uuid (str): UUID of the department to retrieve.
             Returns:
                 ResponseProvider: Success response with department data or 404 if not found.
             """
        try:
            department = DepartmentService().get_by_uuid(dept_uuid)
            return ResponseProvider.success(data=cls._serialize(department))
        except Department.DoesNotExist:
            return ResponseProvider.not_found(
                message=f"Department with UUID {dept_uuid} not found")

    @classmethod
    def get_all_departments(cls, request=None) -> ResponseProvider:
        if request and getattr(request, 'is_line_manager', False) and request.department_scope:
            departments = [request.department_scope]
        else:
            departments = DepartmentService().get_all_departments()
        if not departments:
            return ResponseProvider.success(data=[], message="No departments found")

        data = [cls._serialize(d) for d in departments]
        return ResponseProvider.success(data=data)

    @classmethod
    def update_department(cls, request, dept_uuid: str) -> ResponseProvider:
        """
              Update an existing department.
              Args:
                  request: Django request object containing updated data.
                  dept_uuid (str): UUID of the department to update.
              Returns:
                  ResponseProvider: Success response with updated department data.
              """
        data = get_clean_request_data(
            request,
            allowed_fields={'name', 'description'}
        )

        department = DepartmentService().update_department(
            dept_uuid,
            data,
            triggered_by=request.user,
            request=request
        )
        return ResponseProvider.success(
            message=f"{department.name} updated successfully",
            data=cls._serialize(department)
        )

    @staticmethod
    def delete_department(request, dept_uuid: str) -> ResponseProvider:
        """
              Delete a department by UUID.
              Args:
                  request: Django request object.
                  dept_uuid (str): UUID of the department to delete.
              Returns:
                  ResponseProvider: Success response confirming deletion.
              """
        department = DepartmentService().delete_department(
            dept_uuid,
            triggered_by=request.user,
            request=request
        )
        return ResponseProvider.success(message=f"{department.name} deleted successfully")

    """
        Converting a Department Django model → JSON-safe dictionary
    """
    @staticmethod
    def _serialize(department) -> dict:
        return {
            'uuid': str(department.uuid),
            'name': department.name,
            'description': department.description,
            'created_at': str(department.created_at),

        }
#-----------------------------------------------------------------------------
#         TEAM SERVICE HANDLER
#----------------------------------------------------------------------------
class TeamServiceHandler:
    """
     Handler class for managing team operations.
     Acts as a bridge between API requests and the TeamService.
     Validates and cleans input data, calls service methods,
     and returns standardized responses.
     """

    @classmethod
    def create_team(cls, request) -> ResponseProvider:
        """
               Create a new team.
               Args:
                   request: HTTP request object containing 'team_name' and 'department_uuid'.
               Returns:
                   ResponseProvider: Success response with the created team's data
                                     or error response if creation fails.
               Raises:
                   Any exceptions raised by TeamService are caught and returned via ResponseProvider.
               """
        data = get_clean_request_data(
            request,
            required_fields={'team_name', 'department_uuid'}
        )

        team_name       = data.get('team_name')
        department_uuid = data.get('department_uuid')

        team = TeamService().create_team(
            team_name,
            department_uuid,
            triggered_by=request.user,
            request=request
        )

        return ResponseProvider.created(
            message=f"{team.team_name} team created successfully",
            data=cls._serialize(team)
        )

    @classmethod
    def get_team(cls, team_uuid: str) -> ResponseProvider:
        """
        Retrieve a single team by its UUID.
        Args:
            team_uuid (str): UUID of the team to retrieve.
        Returns:
            ResponseProvider: Success response containing the serialized team data.
        """
        team = TeamService().get_by_uuid(team_uuid)
        return ResponseProvider.success(data=cls._serialize(team))

    @classmethod
    def get_all_teams(cls, request) -> ResponseProvider:
        filters = {
            'department_uuid': request.GET.get('department_uuid'),
        }
        filters = {k: v for k, v in filters.items() if v is not None}

        # Line managers only see teams in their department
        role_name = request.user.role.name if request.user.role else ''
        if role_name in ('Business_Line_Manager', 'Tech_Line_Manager'):
            if request.user.department:
                filters['department_uuid'] = str(request.user.department.uuid)

        teams = TeamService().get_all_teams(**filters)
        data = [cls._serialize(t) for t in teams]
        return ResponseProvider.success(data=data)

    @classmethod
    def update_team(cls, request, team_uuid: str) -> ResponseProvider:
        """
               Update an existing team's information.
               Args:
                   request: HTTP request object containing fields to update ('team_name', 'department_uuid').
                   team_uuid (str): UUID of the team to update.
               Returns:
                   ResponseProvider: Success response with the updated team's serialized data.
               """
        data = get_clean_request_data(
            request,
            allowed_fields={'team_name', 'department_uuid'}
        )

        team = TeamService().update_team(
            team_uuid,
            data,
            triggered_by=request.user,
            request=request
        )
        return ResponseProvider.success(
            message=f"{team.team_name} updated successfully",
            data=cls._serialize(team)
        )

    @staticmethod
    def delete_team(request, team_uuid: str) -> ResponseProvider:
        team = TeamService().delete_team(
            team_uuid,
            triggered_by=request.user,
            request=request
        )
        return ResponseProvider.success(message=f"{team.team_name} deleted successfully")

    @staticmethod
    def assign_user_to_team(request) -> ResponseProvider:
        data = get_clean_request_data(
            request,
            required_fields={'user_uuid', 'team_uuid'}
        )

        user_uuid = data.get('user_uuid')
        team_uuid = data.get('team_uuid')

        team = TeamService().assign_user(
            user_uuid,
            team_uuid,
            triggered_by=request.user,
            request=request
        )
        return ResponseProvider.success(
            message=f"User assigned to {team.team_name} successfully"
        )

    """
        Converting a Team Django model → JSON-safe dictionary
    """
    @staticmethod
    def _serialize(team) -> dict:
        return {
            'uuid': str(team.uuid),
            'team_name': team.team_name,
            'department_uuid': str(team.department.uuid) if team.department else None,
            'department_name': team.department.name if team.department else None,
            'created_at': str(team.created_at),
            'updated_at': str(team.updated_at),
        }
