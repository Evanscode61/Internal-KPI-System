from typing import Any

from utils.decorators.rbac import require_roles,require_permission
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from kpis.services.services import KPIDefinitionHandler, KPIAssignmentHandler, KPIFormulaServiceHandler, \
    KPIResultService
from services.services import KPIService
from services.utils.response_provider import ResponseProvider
from utils.decorators.allowed_http_methods import allowed_http_methods


@csrf_exempt
@allowed_http_methods(['POST'])
@require_roles('admin','Business_Line_Manager','Tech_Line_Manager')
def create_kpi_definition_view(request) -> ResponseProvider :
    try:
        return KPIDefinitionHandler.create_kpi(request)
    except Exception as ex:
        return ResponseProvider.handle_exception(ex)

@csrf_exempt
@allowed_http_methods(['GET'])
@require_roles('admin','Business_Line_Manager','Tech_Line_Manager')
def get_kpi_definition_view(request, kpi_uuid: str) -> ResponseProvider:
    try:
        return KPIDefinitionHandler.get_kpi(kpi_uuid)
    except Exception as ex:
        return ResponseProvider.handle_exception(ex)

@csrf_exempt
@allowed_http_methods(['PATCH', 'PUT'])
@require_roles('admin','Business_Line_Manager','Tech_Line_Manager')
def update_kpi_definition_view(request, kpi_uuid: str) -> ResponseProvider:
    try:
        return KPIDefinitionHandler.update_kpi(request,kpi_uuid)
    except Exception as ex:
        return ResponseProvider.handle_exception(ex)

@csrf_exempt
@allowed_http_methods(['DELETE'])
@require_roles('admin','Business_Line_Manager','Tech_Line_Manager')
def delete_kpi_definition_view(request, kpi_uuid: str) -> ResponseProvider:
    try:
        return KPIDefinitionHandler.delete_kpi(request, kpi_uuid)
    except Exception as ex:
        return ResponseProvider.handle_exception(ex)

@csrf_exempt
@allowed_http_methods(['GET'])
@require_roles( 'hr','admin','Business_Line_Manager','Tech_Line_Manager')
def get_all_kpis_definition_view(request) -> ResponseProvider:
    try:
        return KPIDefinitionHandler.get_all_kpis(request)
    except Exception as ex:
        return ResponseProvider.handle_exception(ex)
# Create your views here.
#________________________________________________________________________________
#
#---------------------------------------------------------------------------------
@csrf_exempt
@allowed_http_methods(['POST'])
@require_roles('admin','Business_Line_Manager','Tech_Line_Manager')
def create_kpi_assignment_view(request) -> ResponseProvider:
    try:
        return KPIAssignmentHandler.assign_kpi(request)
    except Exception as ex:
        return ResponseProvider.handle_exception(ex)

@csrf_exempt
@allowed_http_methods(['PUT', 'PATCH'])
@require_roles('admin','Business_Line_Manager','Tech_Line_Manager')
def update_kpi_assignment_view(request, assignment_uuid:str) -> ResponseProvider:
    try:
        return KPIAssignmentHandler.update_kpi_assignment(request ,assignment_uuid)
    except Exception as ex:
        return ResponseProvider.handle_exception(ex)
@csrf_exempt
@require_roles('admin', 'hr',)
def delete_kpi_assignment_view( request, assignment_uuid):
    try:
        return KPIAssignmentHandler.delete_kpi_assignment(request, assignment_uuid)
    except Exception as ex:
        return ResponseProvider.handle_exception(ex)


@csrf_exempt
@allowed_http_methods(['GET'])
@require_roles("hr",'admin','Business_Line_Manager','Tech_Line_Manager','employee')
def get_kpi_assignments_view(request) -> ResponseProvider:
    try:
        return KPIAssignmentHandler.get_all_kpi_assignments(request)
    except Exception as ex:
        return ResponseProvider.handle_exception(ex)


@csrf_exempt
@allowed_http_methods(['POST'])
@require_roles( "admin",'Business_Line_Manager', 'Tech_Line_Manager')
def create_kpi_formula_view(request) -> ResponseProvider :
    try:
        return KPIFormulaServiceHandler.create_formula(request)
    except Exception as ex:
        return ResponseProvider.handle_exception(ex)

@csrf_exempt
@allowed_http_methods(['PUT', 'PATCH'])
@require_roles( "admin",'Business_Line_Manager', 'Tech_Line_Manager')
def update_kpi_formula_view(request, formula_uuid:str) -> ResponseProvider :
    try:
        return KPIFormulaServiceHandler.update_formula(request, formula_uuid)
    except Exception as ex:
        return ResponseProvider.handle_exception(ex)

@csrf_exempt
@allowed_http_methods(['DELETE'])
@require_roles( "admin",'Business_Line_Manager', 'Tech_Line_Manager')
def delete_kpi_formula_view(request,formula_uuid:str) -> ResponseProvider :
    try:
        return KPIFormulaServiceHandler.delete_formula(request,formula_uuid)
    except Exception as ex:
        return ResponseProvider.handle_exception(ex)

@csrf_exempt
@allowed_http_methods(['GET'])
@require_roles("admin",'Business_Line_Manager', 'Tech_Line_Manager')
def get_kpi_formula_view(request, kpi_uuid: str) -> ResponseProvider:
    try:
        return KPIFormulaServiceHandler.get_formula_by_kpi(request, kpi_uuid)
    except Exception as ex:
        return ResponseProvider.handle_exception(ex)
#-----------------------------------------------------------------------------
#    KPI RESULTS VIEWS
#-----------------------------------------------------------------------------

@csrf_exempt
@allowed_http_methods(['POST'])
@require_roles("admin",'employee', 'Business_Line_Manager', 'Tech_Line_Manager','admin')
def submit_kpi_result_view(request) -> ResponseProvider:
    try:
        return KPIResultService.submit_result(request)
    except Exception as ex:
        return ResponseProvider.handle_exception(ex)


@csrf_exempt
@allowed_http_methods(['GET'])
@require_roles('employee', 'Business_Line_Manager', 'Tech_Line_Manager')
def get_kpi_result_view(request, result_uuid: str) -> ResponseProvider:
    try:
        return KPIResultService.get_result(request,result_uuid)
    except Exception as ex:
        return ResponseProvider.handle_exception(ex)


@csrf_exempt
@allowed_http_methods(['GET'])
@require_roles('hr','admin','Business_Line_Manager','Tech_Line_Manager','employee')
def get_all_kpi_results_view(request) -> ResponseProvider:
    try:
        return KPIResultService.get_all_results(request)
    except Exception as ex:
        return ResponseProvider.handle_exception(ex)


@csrf_exempt
@allowed_http_methods(['PUT','PATCH'])
@require_roles('admin', 'Business_Line_Manager', 'Tech_Line_Manager','employee')
def update_kpi_result_view(request, result_uuid: str) -> ResponseProvider:
    try:
        return KPIResultService.update_result(request, result_uuid)
    except Exception as ex:
        return ResponseProvider.handle_exception(ex)


@csrf_exempt
@allowed_http_methods(['GET'])
@require_roles('hr','admin')
def export_kpi_results_csv_view(request) -> ResponseProvider:
    try:
        return KPIResultService.export_results_csv(request)
    except Exception as ex:
        return ResponseProvider.handle_exception(ex)

@csrf_exempt
@allowed_http_methods(['PATCH'])
@require_roles('Business_Line_Manager', 'Tech_Line_Manager', 'admin', 'hr')
def approve_reject_kpi_result_view(request, result_uuid: str) -> ResponseProvider:
    try:
        return KPIResultService.approve_reject_result(request, result_uuid)
    except Exception as ex:
        return ResponseProvider.handle_exception(ex)



