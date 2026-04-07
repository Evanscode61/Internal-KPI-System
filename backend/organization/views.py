from typing import Any

from django.views.decorators.csrf import csrf_exempt

from organization.services.services import TeamServiceHandler, DepartmentServiceHandler
from services.utils.response_provider import ResponseProvider
from utils.decorators.allowed_http_methods import allowed_http_methods
from utils.decorators.rbac import require_roles


@csrf_exempt
@allowed_http_methods(['POST'])
@require_roles("admin","hr")
def create_department_view(request) -> ResponseProvider | Any:
    try:
        return DepartmentServiceHandler.create_department(request)
    except Exception as ex:
        return ResponseProvider.handle_exception(ex)


@csrf_exempt
@allowed_http_methods(['GET'])
@require_roles("admin","hr")
def get_department_view(request, dept_uuid: str) -> ResponseProvider | Any:
    try:
        return DepartmentServiceHandler.get_department(dept_uuid)
    except Exception as ex:
        return ResponseProvider.handle_exception(ex)


@csrf_exempt
@allowed_http_methods(['GET'])
@require_roles("admin","hr","Tech_Line_Manager","Business_Line_Manager","hr")
def get_all_departments_view(request) -> ResponseProvider | Any:
    try:
        return DepartmentServiceHandler.get_all_departments(request)
    except Exception as ex:
        return ResponseProvider.handle_exception(ex)


@csrf_exempt
@allowed_http_methods(['PATCH', 'PUT'])
@require_roles("admin","hr")
def update_department_view(request, dept_uuid: str) -> ResponseProvider | Any:
    try:
        return DepartmentServiceHandler.update_department(request, dept_uuid)
    except Exception as ex:
        return ResponseProvider.handle_exception(ex)


@csrf_exempt
@allowed_http_methods(['DELETE'])
@require_roles("admin","hr")
def delete_department_view(request, dept_uuid: str) -> ResponseProvider | Any:
    try:
        return DepartmentServiceHandler.delete_department(request, dept_uuid)
    except Exception as ex:
        return ResponseProvider.handle_exception(ex)


# =============================================================================
# TEAM VIEWS
# =============================================================================

@csrf_exempt
@allowed_http_methods(['POST'])
@require_roles("admin","hr")
def create_team_view(request) -> ResponseProvider | Any:
    try:
        return TeamServiceHandler.create_team(request)
    except Exception as ex:
        return ResponseProvider.handle_exception(ex)


@csrf_exempt
@allowed_http_methods(['GET'])
@require_roles("admin","hr")
def get_team_view(request, team_uuid: str) -> ResponseProvider | Any:
    try:
        return TeamServiceHandler.get_team(team_uuid)
    except Exception as ex:
        return ResponseProvider.handle_exception(ex)


@csrf_exempt
@allowed_http_methods(['GET'])
@require_roles("admin","Tech_Line_Manager","Business_Line_Manager","hr")
def get_all_teams_view(request) -> ResponseProvider | Any:
    try:
        return TeamServiceHandler.get_all_teams(request)
    except Exception as ex:
        return ResponseProvider.handle_exception(ex)


@csrf_exempt
@allowed_http_methods(['PATCH', 'PUT'])
@require_roles("admin","hr")
def update_team_view(request, team_uuid: str) -> ResponseProvider | Any:
    try:
        return TeamServiceHandler.update_team(request, team_uuid)
    except Exception as ex:
        return ResponseProvider.handle_exception(ex)


@csrf_exempt
@allowed_http_methods(['DELETE'])
@require_roles("admin")
def delete_team_view(request, team_uuid: str) -> ResponseProvider | Any:
    try:
        return TeamServiceHandler.delete_team(request, team_uuid)
    except Exception as ex:
        return ResponseProvider.handle_exception(ex)


@csrf_exempt
@allowed_http_methods(['POST'])
@require_roles("admin","hr")
def assign_user_to_team_view(request) -> ResponseProvider | Any:
    try:
        return TeamServiceHandler.assign_user_to_team(request)
    except Exception as ex:
        return ResponseProvider.handle_exception(ex)