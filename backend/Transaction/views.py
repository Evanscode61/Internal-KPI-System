from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from Transaction.services.services import TransactionLogHandler
from services.utils.response_provider import ResponseProvider
from utils.decorators.allowed_http_methods import allowed_http_methods
from utils.decorators.rbac import require_roles


@csrf_exempt
@allowed_http_methods(['GET'])
@require_roles('admin', 'hr')
def get_all_logs_view(request):
    """
    Retrieve all transaction logs with optional filters (GET).
    Supports query params: user_uuid, action, object_type, time_from, time_to.
    Restricted to admin and hr only.
    """
    try:
        return TransactionLogHandler.get_all_logs(request)
    except Exception as ex:
        return ResponseProvider.handle_exception(ex)


@csrf_exempt
@allowed_http_methods(['GET'])
@require_roles('admin', 'hr')
def get_log_view(request, log_uuid: str):
    """
    Retrieve a single transaction log by UUID (GET).
    Restricted to admin and hr only.
    """
    try:
        return TransactionLogHandler.get_log(log_uuid)
    except Exception as ex:
        return ResponseProvider.handle_exception(ex)

# Create your views here.
