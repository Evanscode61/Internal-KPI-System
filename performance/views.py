from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model

from performance.models import Notification
from performance.services.dashboard_service import DashboardService
from performance.services.performanceservice import PerformanceSummaryService
from services.utils.response_provider import ResponseProvider
from utils.decorators.allowed_http_methods import allowed_http_methods
from utils.decorators.rbac import require_roles

User = get_user_model()


# ── PERFORMANCE SUMMARY VIEWS ─────────────────────────────────────────────────

@csrf_exempt
@allowed_http_methods(['POST'])
@require_roles('admin', 'hr', 'Business_Line_Manager', 'Tech_Line_Manager')
def generate_summary_view(request):
    """
        Generate a performance summary for a user, team, or department (POST).
        Restricted to admin and hr only.
        """
    try:
        return PerformanceSummaryService.generate_summary(request)
    except Exception as ex:
        return ResponseProvider.handle_exception(ex)


@csrf_exempt
@allowed_http_methods(['GET'])
@require_roles('admin', 'hr', 'Business_Line_Manager', 'Tech_Line_Manager', 'employee')
def get_summary_view(request, summary_uuid: str):
    """
       Retrieve a single performance summary by UUID (GET).
       Access is role-scoped, employees see only their own,
       line managers see their department only, admin/hr see all.
       """
    try:
        return PerformanceSummaryService.get_summary(request, summary_uuid)
    except Exception as ex:
        return ResponseProvider.handle_exception(ex)


@csrf_exempt
@allowed_http_methods(['GET'])
@require_roles('admin', 'hr', 'Business_Line_Manager', 'Tech_Line_Manager','employee')
def get_all_summaries_view(request):
    try:
        return PerformanceSummaryService.get_all_summaries(request)
    except Exception as ex:
        return ResponseProvider.handle_exception(ex)


@csrf_exempt
@allowed_http_methods(['GET'])
@require_roles('admin', 'hr', 'Business_Line_Manager', 'Tech_Line_Manager')
def export_summaries_csv_view(request):
    try:
        return PerformanceSummaryService.export_summaries_csv(request)
    except Exception as ex:
        return ResponseProvider.handle_exception(ex)

@csrf_exempt
@allowed_http_methods(['DELETE'])
@require_roles('admin', 'hr', 'Business_Line_Manager', 'Tech_Line_Manager','employee')
def delete_summary_view(request, summary_uuid: str):
    try:
        return PerformanceSummaryService.delete_summary(request, summary_uuid)
    except Exception as ex:
        return ResponseProvider.handle_exception(ex)


# ── NOTIFICATION VIEWS

@csrf_exempt
@allowed_http_methods(['GET'])
@require_roles('admin', 'hr', 'Business_Line_Manager', 'Tech_Line_Manager', 'employee')
def get_notifications_view(request):
    """
    Returns all unread notifications for the logged in user.
    Every role can access this — each user only sees their own.
    """
    try:
        notifications = Notification.objects.filter(
            recipient = request.user,
            is_read   = False,
        ).select_related('alert', 'summary').order_by('-created_at')

        data = [{
            'id':                n.id,
            'notification_type': n.notification_type,
            'message':           n.message,
            'is_read':           n.is_read,
            'created_at':        str(n.created_at),
            'alert_type':        n.alert.alert_type if n.alert else None,
            'kpi_name':          n.alert.kpi_assignment.kpi.kpi_name if n.alert else None,
            'summary_type':      n.summary.summary_type if n.summary else None,
        } for n in notifications]

        return ResponseProvider.success(
            message = f'{len(data)} unread notifications',
            data    = data
        )
    except Exception as ex:
        return ResponseProvider.handle_exception(ex)


@csrf_exempt
@allowed_http_methods(['GET'])
@require_roles('admin', 'hr', 'Business_Line_Manager', 'Tech_Line_Manager', 'employee')
def get_all_notifications_view(request):
    """
    Returns all notifications for the logged in user
    both read and unread. Useful for notification history.
    """
    try:
        notifications = Notification.objects.filter(
            recipient = request.user,
        ).select_related('alert', 'summary').order_by('-created_at')

        data = [{
            'id':                n.id,
            'notification_type': n.notification_type,
            'message':           n.message,
            'is_read':           n.is_read,
            'created_at':        str(n.created_at),
            'alert_type':        n.alert.alert_type if n.alert else None,
            'kpi_name':          n.alert.kpi_assignment.kpi.kpi_name if n.alert else None,
            'summary_type':      n.summary.summary_type if n.summary else None,
        } for n in notifications]

        return ResponseProvider.success(
            message = f'{len(data)} notifications found',
            data    = data
        )
    except Exception as ex:
        return ResponseProvider.handle_exception(ex)


@csrf_exempt
@allowed_http_methods(['PATCH'])
@require_roles('admin', 'hr', 'Business_Line_Manager', 'Tech_Line_Manager', 'employee')
def mark_notification_read_view(request, notification_id: int):
    """
    Mark a single notification as read.
    Users can only mark their own notifications.
    """
    try:
        notification = Notification.objects.get(
            id        = notification_id,
            recipient = request.user,   # ensures users can only mark their own
        )
        notification.is_read = True
        notification.save(update_fields=['is_read'])

        return ResponseProvider.success(
            message = 'Notification marked as read'
        )
    except Notification.DoesNotExist:
        return ResponseProvider.not_found(
            error = 'Notification not found'
        )
    except Exception as ex:
        return ResponseProvider.handle_exception(ex)


@csrf_exempt
@allowed_http_methods(['PATCH'])
@require_roles('admin', 'hr', 'Business_Line_Manager', 'Tech_Line_Manager', 'employee')
def mark_all_notifications_read_view(request):
    """
    Mark all of the logged in user's notifications as read at once.
    Useful for a 'mark all as read' button in the frontend.
    """
    try:
        updated = Notification.objects.filter(
            recipient = request.user,
            is_read   = False,
        ).update(is_read=True)

        return ResponseProvider.success(
            message = f'{updated} notifications marked as read'
        )
    except Exception as ex:
        return ResponseProvider.handle_exception(ex)


@csrf_exempt
@allowed_http_methods(['GET'])
@require_roles('admin', 'hr', 'Business_Line_Manager', 'Tech_Line_Manager', 'employee')
def dashboard_view(request):
    """
    Return a role-scoped performance dashboard (GET).
    Optional query parameters are period start and period end.
    Response scope by role:
    admin / hr can see full company dashboard
    Business/Tech LM can see department-scoped dashboard
    employee can see personal dashboard
    Returns a structured snapshot including overview stats,
    department/team breakdowns, alert summary, top performers,
    and employees needing attention — all in one call.
    """
    try:
        data = DashboardService.get_dashboard(request)
        if data is None:
            return ResponseProvider.forbidden(
                error='You do not have permission to view the dashboard'
            )
        return ResponseProvider.success(
            message='Dashboard data retrieved successfully',
            data=data
        )
    except Exception as ex:
        return ResponseProvider.handle_exception(ex)

@csrf_exempt
@allowed_http_methods(['DELETE'])
@require_roles('admin', 'hr', 'Business_Line_Manager', 'Tech_Line_Manager', 'employee')
def delete_notification_view(request, notification_id: int):
    try:
        notification = Notification.objects.get(
            id        = notification_id,
            recipient = request.user,
        )
        notification.delete()
        return ResponseProvider.success(message='Notification deleted')
    except Notification.DoesNotExist:
        return ResponseProvider.not_found(error='Notification not found')
    except Exception as ex:
        return ResponseProvider.handle_exception(ex)