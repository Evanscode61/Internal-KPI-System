from typing import Any

from django.views.decorators.csrf import csrf_exempt

from organization.services.services import TeamServiceHandler, DepartmentServiceHandler
from services.utils.response_provider import ResponseProvider
from utils.decorators.allowed_http_methods import allowed_http_methods


@csrf_exempt
@allowed_http_methods(['POST'])
def create_department_view(request) -> ResponseProvider | Any:
    try:
        return DepartmentServiceHandler.create_department(request)
    except Exception as ex:
        return ResponseProvider.handle_exception(ex)


@csrf_exempt
@allowed_http_methods(['GET'])
def get_department_view(request, dept_uuid: str) -> ResponseProvider | Any:
    try:
        return DepartmentServiceHandler.get_department(dept_uuid)
    except Exception as ex:
        return ResponseProvider.handle_exception(ex)


@csrf_exempt
@allowed_http_methods(['GET'])
def get_all_departments_view(request) -> ResponseProvider | Any:
    try:
        return DepartmentServiceHandler.get_all_departments()
    except Exception as ex:
        return ResponseProvider.handle_exception(ex)


@csrf_exempt
@allowed_http_methods(['PATCH', 'PUT'])
def update_department_view(request, dept_uuid: str) -> ResponseProvider | Any:
    try:
        return DepartmentServiceHandler.update_department(request, dept_uuid)
    except Exception as ex:
        return ResponseProvider.handle_exception(ex)


@csrf_exempt
@allowed_http_methods(['DELETE'])
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
def create_team_view(request) -> ResponseProvider | Any:
    try:
        return TeamServiceHandler.create_team(request)
    except Exception as ex:
        return ResponseProvider.handle_exception(ex)


@csrf_exempt
@allowed_http_methods(['GET'])
def get_team_view(request, team_uuid: str) -> ResponseProvider | Any:
    try:
        return TeamServiceHandler.get_team(team_uuid)
    except Exception as ex:
        return ResponseProvider.handle_exception(ex)


@csrf_exempt
@allowed_http_methods(['GET'])
def get_all_teams_view(request) -> ResponseProvider | Any:
    try:
        return TeamServiceHandler.get_all_teams(request)
    except Exception as ex:
        return ResponseProvider.handle_exception(ex)


@csrf_exempt
@allowed_http_methods(['PATCH', 'PUT'])
def update_team_view(request, team_uuid: str) -> ResponseProvider | Any:
    try:
        return TeamServiceHandler.update_team(request, team_uuid)
    except Exception as ex:
        return ResponseProvider.handle_exception(ex)


@csrf_exempt
@allowed_http_methods(['DELETE'])
def delete_team_view(request, team_uuid: str) -> ResponseProvider | Any:
    try:
        return TeamServiceHandler.delete_team(request, team_uuid)
    except Exception as ex:
        return ResponseProvider.handle_exception(ex)


@csrf_exempt
@allowed_http_methods(['POST'])
def assign_user_to_team_view(request) -> ResponseProvider | Any:
    try:
        return TeamServiceHandler.assign_user_to_team(request)
    except Exception as ex:
        return ResponseProvider.handle_exception(ex)