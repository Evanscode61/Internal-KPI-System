from typing import Any

import data
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from kpis.services.services import KPIDefinitionHandler,KPIAssignmentHandler
from services.services import KPIService
from services.utils.response_provider import ResponseProvider
from utils.decorators.allowed_http_methods import allowed_http_methods


@csrf_exempt
@allowed_http_methods(['POST'])
def create_kpi_definition_view(request) -> ResponseProvider :
    try:
        return KPIDefinitionHandler.create_kpi(request)
    except Exception as ex:
        return ResponseProvider.handle_exception(ex)

@csrf_exempt
@allowed_http_methods(['GET'])
def get_kpi_definition_view(request, kpi_uuid: str) -> ResponseProvider:
    try:
        return KPIDefinitionHandler.get_kpi(kpi_uuid)
    except Exception as ex:
        return ResponseProvider.handle_exception(ex)

@csrf_exempt
@allowed_http_methods(['PATCH', 'PUT'])
def update_kpi_definition_view(request, kpi_uuid: str) -> ResponseProvider:
    try:
        return KPIDefinitionHandler.update_kpi(request,kpi_uuid)
    except Exception as ex:
        return ResponseProvider.handle_exception(ex)

@csrf_exempt
@allowed_http_methods(['DELETE'])
def delete_kpi_definition_view(request, kpi_uuid: str) -> ResponseProvider:
    try:
        return KPIDefinitionHandler.delete_kpi(request, kpi_uuid)
    except Exception as ex:
        return ResponseProvider.handle_exception(ex)

@csrf_exempt
@allowed_http_methods(['GET'])
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
def create_kpi_assignment_view(request) -> ResponseProvider:
    try:
        return KPIAssignmentHandler.assign_kpi(request)
    except Exception as ex:
        return ResponseProvider.handle_exception(ex)

@csrf_exempt
@allowed_http_methods(['PUT', 'PATCH'])
def update_kpi_assignment_view(request) -> ResponseProvider:
    try:
        return KPIAssignmentHandler.update_kpi_assignment(request)
    except Exception as ex:
        return ResponseProvider.handle_exception(ex)

@csrf_exempt
@allowed_http_methods(['GET'])
def get_kpi_assignments_view(request) -> ResponseProvider:
    try:
        return KPIAssignmentHandler.get_all_kpi_assignments(request)
    except Exception as ex:
        return ResponseProvider.handle_exception(ex)



