"""
AlertResolutionService
──────────────────────
Handles fetching and resolving KPI alerts.
Role scoping:
    admin/hr    → see and resolve all alerts
    BLM/TLM     → see and resolve only their department alerts
"""

import json
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth import get_user_model

from performance.models import KPIAlert
from services.utils.response_provider import ResponseProvider

User = get_user_model()


class AlertResolutionService:

    # Serialize

    @staticmethod
    def _serialize(alert) -> dict:
        return {
            'id':              alert.id,
            'alert_type':      alert.alert_type,
            'message':         alert.message,
            'threshold':       float(alert.threshold) if alert.threshold else None,
            'is_resolved':     alert.is_resolved,
            'resolved_at':     alert.resolved_at.strftime('%Y-%m-%d %H:%M') if alert.resolved_at else None,
            'resolved_by':     alert.resolved_by.username if alert.resolved_by else None,
            'resolution_note': alert.resolution_note or '',
            'kpi_name':        alert.kpi_assignment.kpi.kpi_name if alert.kpi_assignment else None,
            'notified_user':   alert.notified_user.username    if alert.notified_user    else None,
            'notified_team':   alert.notified_team.team_name   if alert.notified_team    else None,
            'notified_dept':   alert.notified_department.name  if alert.notified_department else None,
        }

    # scoping of the alerts

    @staticmethod
    def _is_manager(user):
        return bool(user.role and user.role.is_manager)

    @staticmethod
    def _get_alert_dept(alert):
        return (
            alert.notified_user.department       if alert.notified_user       else
            alert.notified_team.department       if alert.notified_team       else
            alert.notified_department            if alert.notified_department else None
        )
    
    @classmethod
    def _get_scoped_queryset(cls, user):
        qs = KPIAlert.objects.select_related(
            'kpi_assignment__kpi', 'notified_user',
            'notified_team', 'notified_department', 'resolved_by'
        )
        if cls._is_manager(user):
            qs = qs.filter(
                Q(notified_user__department=user.department) |
                Q(notified_team__department=user.department) |
                Q(notified_department=user.department)
            )
        return qs.order_by('is_resolved', '-id')

    @classmethod
    def get_all_alerts(cls, request) -> ResponseProvider:
        """Return all alerts scoped by role."""
        alerts = cls._get_scoped_queryset(request.user)
        return ResponseProvider.success(
            message=f'{alerts.count()} alerts found',
            data=[cls._serialize(a) for a in alerts]
        )

    @classmethod
    def resolve_alert(cls, request, alert_id: int) -> ResponseProvider:
        """Resolve a single alert with an optional resolution note."""
        body = json.loads(request.body or '{}')

        try:
            alert = KPIAlert.objects.select_related(
                'notified_user', 'notified_team', 'notified_department'
            ).get(id=alert_id)
        except KPIAlert.DoesNotExist:
            return ResponseProvider.not_found(error='Alert not found')

        if cls._is_manager(request.user):
            alert_dept = cls._get_alert_dept(alert)
            if alert_dept != request.user.department:
                return ResponseProvider.forbidden(
                    message='You can only resolve alerts in your department'
                )

        if alert.is_resolved:
            return ResponseProvider.bad_request(message='Alert already resolved')

        alert.is_resolved = True
        alert.resolved_at = timezone.now()
        alert.resolved_by = request.user
        alert.resolution_note = body.get('resolution_note', '')
        alert.save(update_fields=[
            'is_resolved', 'resolved_at', 'resolved_by', 'resolution_note'
        ])

        return ResponseProvider.success(
            message='Alert resolved successfully',
            data=cls._serialize(alert)
        )

    @classmethod
    def resolve_all_alerts(cls, request) -> ResponseProvider:
        """Resolve all unresolved alerts scoped by role."""
        alerts = KPIAlert.objects.filter(is_resolved=False)
        if cls._is_manager(request.user):
            dept = request.user.department
            alerts = alerts.filter(
                Q(notified_user__department=dept) |
                Q(notified_team__department=dept) |
                Q(notified_department=dept)
            )

        count = alerts.count()
        alerts.update(
            is_resolved=True,
            resolved_at=timezone.now(),
            resolved_by=request.user,
            resolution_note='Alert resolved successfully',
        )
        return ResponseProvider.success(message=f'{count} alerts resolved successfully')