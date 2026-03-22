from django.contrib.auth import get_user_model
from services.services import PerformanceSummaryAccountService
from services.utils.response_provider import ResponseProvider
from utils.common import get_clean_request_data
from kpis.models import KPIResults

from organization.models import Department
from performance.models import PerformanceSummary

User = get_user_model()

ROLE_DEPARTMENT_MAP = {
    'business_line_manager': 'business',
    'tech_line_manager': 'tech',
}
HR_ADMIN_ROLES = {'hr', 'admin'}


class PerformanceSummaryService:

    # ── GENERATE ──────────────────────────────────────────────────────────────

    @classmethod
    def generate_summary(cls, request):
        """
        Routes the generate request to the correct method
        based on summary_type provided in the request body.
        """
        data = get_clean_request_data(
            request,
            required_fields={'summary_type', 'period_start', 'period_end'}
        )

        summary_type = data.get('summary_type')
        period_start = data.get('period_start')
        period_end   = data.get('period_end')
        service      = PerformanceSummaryAccountService()

        if summary_type == 'individual':
            if not data.get('user_uuid'):
                return ResponseProvider.bad_request(
                    error='user_uuid is required for individual summary'
                )
            summary = service.generate_individual_summary(
                data['user_uuid'],
                period_start,
                period_end,
                triggered_by = request.user,
                request      = request,
            )

        elif summary_type == 'team':
            if not data.get('team_uuid'):
                return ResponseProvider.bad_request(
                    error='team_uuid is required for team summary'
                )
            summary = service.generate_team_summary(
                data['team_uuid'],
                period_start,
                period_end,
                triggered_by = request.user,
                request      = request,
            )

        elif summary_type == 'department':
            if not data.get('department_uuid'):
                return ResponseProvider.bad_request(
                    error='department_uuid is required for department summary'
                )
            # Line managers can only generate summaries for their own department
            role = request.user.role.name.lower() if request.user.role else None
            if role in ROLE_DEPARTMENT_MAP:
                if not request.user.department or \
                   str(request.user.department.uuid) != data['department_uuid']:
                    return ResponseProvider.forbidden(
                        error='You can only generate summaries for your own department'
                    )
            summary = service.generate_department_summary(
                data['department_uuid'],
                period_start,
                period_end,
                triggered_by = request.user,
                request      = request,
            )

        else:
            return ResponseProvider.bad_request(
                error="summary_type must be 'individual', 'team', or 'department'"
            )

        return ResponseProvider.created(
            message = 'Performance summary generated successfully',
            data    = cls._serialize(summary)
        )

    # ── GET ONE ───────────────────────────────────────────────────────────────

    @classmethod
    def get_summary(cls, request, summary_uuid):
        """
        Fetch a single summary by UUID.
        Access rules:
            employee          → own individual summary only
            line manager      → any summary within their department
            hr / admin        → all summaries
        """
        summary = PerformanceSummaryAccountService().get_by_uuid(summary_uuid)
        role    = request.user.role.name.lower() if request.user.role else None

        if role == 'employee':
            # Employee can only see their own individual summary
            if summary.summary_type != 'individual' or summary.user != request.user:
                return ResponseProvider.forbidden(
                    error='You may only view your own individual summary'
                )

        elif role in ROLE_DEPARTMENT_MAP:
            # Line manager can see all summary types but only
            # within their own department
            if not summary.department or summary.department != request.user.department:
                return ResponseProvider.forbidden(
                    error='You may only view summaries within your department'
                )

        elif role in HR_ADMIN_ROLES:
            pass  # unrestricted — HR and admin see everything

        else:
            return ResponseProvider.forbidden(error='Access denied')

        return ResponseProvider.success(data=cls._serialize(summary))

    # ── GET ALL ───────────────────────────────────────────────────────────────

    @classmethod
    def get_all_summaries(cls, request):
        """
        Return a list of summaries scoped to the requesting
        user's role and any query filters passed as query params.
        """
        filters = {
            'user_uuid':       request.GET.get('user_uuid'),
            'team_uuid':       request.GET.get('team_uuid'),
            'department_uuid': request.GET.get('department_uuid'),
            'period_start':    request.GET.get('period_start'),
            'period_end':      request.GET.get('period_end'),
            'summary_type':    request.GET.get('summary_type'),
        }
        filters = {k: v for k, v in filters.items() if v is not None}
        filters = cls._apply_role_filters(request, filters)

        if filters is None:
            return ResponseProvider.forbidden(
                error='You do not have permission to view these summaries'
            )

        summaries = PerformanceSummaryAccountService().get_all_summaries(**filters)
        return ResponseProvider.success(
            data=[cls._serialize(s) for s in summaries]
        )

    # ── EXPORT CSV ────────────────────────────────────────────────────────────

    @classmethod
    def export_summaries_csv(cls, request):
        """Export summaries as CSV scoped to the requesting user's role."""
        filters = {
            'department_uuid': request.GET.get('department_uuid'),
            'team_uuid':       request.GET.get('team_uuid'),
            'period_start':    request.GET.get('period_start'),
            'period_end':      request.GET.get('period_end'),
            'summary_type':    request.GET.get('summary_type'),
        }
        filters = {k: v for k, v in filters.items() if v is not None}
        filters = cls._apply_role_filters(request, filters)

        if filters is None:
            return ResponseProvider.forbidden(
                error='You do not have permission to export these summaries'
            )

        return PerformanceSummaryAccountService().export_csv(**filters)

    @classmethod
    def delete_summary(cls, request, summary_uuid):
        summary = PerformanceSummaryAccountService().get_by_uuid(summary_uuid)

        role = request.user.role.name.lower() if request.user.role else ''

        # Manager can only delete summaries within their own department
        if role in ('business_line_manager', 'tech_line_manager'):
            if not summary.department or summary.department != request.user.department:
                return ResponseProvider.forbidden(
                    error='You can only delete summaries within your department'
                )

        summary.delete()
        return ResponseProvider.success(message='Summary deleted successfully')

    # ── ROLE FILTER ───────────────────────────────────────────────────────────

    @classmethod
    def _apply_role_filters(cls, request, filters):
        """
        Scopes the filters to what the requesting user is allowed to see.
        Returns None if the role has no access at all.
        """
        role = request.user.role.name.lower() if request.user.role else None

        if role == 'employee':
            # Employee can only ever see their own individual summary
            filters['user_uuid']    = str(request.user.uuid)
            filters['summary_type'] = 'individual'

        elif role in ROLE_DEPARTMENT_MAP:
            # Line manager is locked to their own department.
            # Use the actual department FK on the user — not a hardcoded name string.
            # This works regardless of what the department is called.
            if request.user.department:
                filters['department_uuid'] = str(request.user.department.uuid)
                filters.pop('department_name', None)
            else:
                # Manager has no department assigned — return nothing
                filters['department_uuid'] = 'none'

        elif role in HR_ADMIN_ROLES:
            pass  # unrestricted

        else:
            return None

        return filters

    # ── SERIALIZE ─────────────────────────────────────────────────────────────

    @staticmethod
    def _serialize(summary):
        base = {
            'uuid': str(summary.uuid),
            'summary_type': summary.summary_type,
            'period_start': str(summary.period_start),
            'period_end': str(summary.period_end),
            'weighted_score': str(summary.weighted_score),
            'rating': summary.rating,
            'created_at': str(summary.created_at),
            'updated_at': str(summary.updated_at),
        }

        # ── KPI breakdown — fetch approved results that make up this summary
        if summary.summary_type == 'individual' and summary.user:
            results = KPIResults.objects.filter(
                submitted_by=summary.user,
                kpi_assignment__assigned_to=summary.user,
                created_at__gte=summary.period_start,
                created_at__lte=summary.period_end,
                approval_status='approved',
                calculated_score__isnull=False,
            ).select_related('kpi_assignment__kpi')

        elif summary.summary_type == 'team' and summary.team:
            results = KPIResults.objects.filter(
                kpi_assignment__assigned_team=summary.team,
                created_at__gte=summary.period_start,
                created_at__lte=summary.period_end,
                approval_status='approved',
                calculated_score__isnull=False,
            ).select_related('kpi_assignment__kpi')

        elif summary.summary_type == 'department' and summary.department:
            results = KPIResults.objects.filter(
                kpi_assignment__assigned_department=summary.department,
                created_at__gte=summary.period_start,
                created_at__lte=summary.period_end,
                approval_status='approved',
                calculated_score__isnull=False,
            ).select_related('kpi_assignment__kpi')
        else:
            results = []

        base['kpi_breakdown'] = [
            {
                'kpi_name': r.kpi_assignment.kpi.kpi_name,
                'actual_value': str(r.actual_value),
                'calculated_score': str(r.calculated_score),
                'rating': r.rating,
                'weight': float(r.kpi_assignment.kpi.weight_value or 1),
                'measurement_type': r.kpi_assignment.kpi.measurement_type,
                'submitted_by': r.submitted_by.username if r.submitted_by else None,
            }
            for r in results
        ]

        # ── Type specific fields
        if summary.summary_type == 'individual':
            base.update({
                'user_uuid': str(summary.user.uuid) if summary.user else None,
                'username': summary.user.username if summary.user else None,
                'department_name': summary.department.name if summary.department else None,
                'team_name': summary.team.team_name if summary.team else None,
            })
        elif summary.summary_type == 'team':
            base.update({
                'team_uuid': str(summary.team.uuid) if summary.team else None,
                'team_name': summary.team.team_name if summary.team else None,
                'department_name': summary.department.name if summary.department else None,
            })
        elif summary.summary_type == 'department':
            base.update({
                'department_uuid': str(summary.department.uuid) if summary.department else None,
                'department_name': summary.department.name if summary.department else None,
            })

        return base