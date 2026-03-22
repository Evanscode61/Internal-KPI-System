"""
DashboardService
────────────────
Aggregates data from KPIResults, PerformanceSummary, KPIAlert,
KpiAssignment, Department, and Team into a single structured
snapshot. No new models required — queries what already exists.

Role scoping:
    admin / hr can see full company-wide dashboard
    Business/Tech LM are scoped to their department only
    employee can see their own personal dashboard only
"""

from django.contrib.auth import get_user_model
from django.db.models import Avg, Count, Q

from kpis.models import KPIResults, KpiAssignment
from organization.models import Department, Team
from performance.models import KPIAlert, PerformanceSummary

User = get_user_model()

HR_ADMIN_ROLES   = {'hr', 'admin'}
RATING_ORDER     = ['outstanding', 'good', 'satisfactory', 'needs_improvement', 'poor']


class DashboardService:

    @classmethod
    def get_dashboard(cls, request):
        """
        Main entry point. Routes to the correct dashboard scope
        based on the requesting user's role.
        """
        role = request.user.role.name.lower() if request.user.role else None
        period_start = request.GET.get('period_start')
        period_end   = request.GET.get('period_end')

        if role in HR_ADMIN_ROLES:
            return cls._company_dashboard(period_start, period_end)


        elif request.user.role and request.user.role.is_manager and request.user.department:

            return cls._department_dashboard(request.user, period_start, period_end)

        elif role == 'employee':
            return cls._employee_dashboard(request.user, period_start, period_end)

        else:
            return None  # caller handles forbidden

    #  COMPANY DASHBOARD to be viewed by admin/hr

    @classmethod
    def _company_dashboard(cls, period_start=None, period_end=None):
        """
        Full company-wide snapshot. Aggregates across all departments,
        teams, and employees. Restricted to admin and hr.
        """
        results_qs     = cls._filter_results(period_start, period_end)
        assignments_qs = cls._filter_assignments(period_start, period_end)
        alerts_qs      = KPIAlert.objects.all()

        return {
            'scope':            'company',
            'period':           cls._period_label(period_start, period_end),
            'company_overview': cls._build_overview(results_qs, assignments_qs),
            'departments':      cls._build_department_breakdown(
                                    Department.objects.all(),
                                    period_start, period_end
                                ),
            'alerts_summary':   cls._build_alerts_summary(alerts_qs),
            'top_performers':   cls._build_top_performers(results_qs, limit=5),
            'needs_attention':  cls._build_needs_attention(results_qs, limit=5),
        }

    # DEPARTMENT DASHBOARD  scoped to respective line managers

    @classmethod
    def _department_dashboard(cls, user, period_start=None, period_end=None):
        """
        Department scoped snapshot for line managers.
        Only shows data within the manager's own department.
        """
        department = user.department
        if not department:
            return {
                'scope':   'department',
                'warning': 'You are not assigned to a department',
                'data':    {}
            }

        results_qs = cls._filter_results(period_start, period_end).filter(
            kpi_assignment__assigned_department=department
        ) | cls._filter_results(period_start, period_end).filter(
            kpi_assignment__assigned_to__department=department
        ) | cls._filter_results(period_start, period_end).filter(
            kpi_assignment__assigned_team__department=department
        )

        assignments_qs = cls._filter_assignments(period_start, period_end).filter(
            Q(assigned_department=department) |
            Q(assigned_to__department=department) |
            Q(assigned_team__department=department)
        )

        alerts_qs = KPIAlert.objects.filter(
            Q(notified_department=department) |
            Q(notified_team__department=department) |
            Q(notified_user__department=department)
        )

        teams = Team.objects.filter(department=department)

        return {
            'scope':             'department',
            'department':        department.name,
            'period':            cls._period_label(period_start, period_end),
            'overview':          cls._build_overview(results_qs, assignments_qs),
            'teams':             cls._build_team_breakdown(
                                     teams, period_start, period_end
                                 ),
            'alerts_summary':    cls._build_alerts_summary(alerts_qs),
            'top_performers':    cls._build_top_performers(results_qs, limit=5),
            'needs_attention':   cls._build_needs_attention(results_qs, limit=5),
        }

    #EMPLOYEE DASHBOARD scoped to individual employee

    @classmethod
    def _employee_dashboard(cls, user, period_start=None, period_end=None):
        """
        Personal dashboard for an individual employee.
        Shows only their own KPI results, scores, and notifications.
        """
        results_qs = cls._filter_results(period_start, period_end).filter(
            submitted_by=user
        )

        assignments_qs = cls._filter_assignments(period_start, period_end).filter(
            assigned_to=user
        )

        summaries = PerformanceSummary.objects.filter(
            user=user,
            summary_type='individual',
        ).order_by('-period_end')

        unread_notifications = user.notifications.filter(is_read=False).count()

        return {
            'scope':                  'employee',
            'username':               user.username,
            'department':             user.department.name if user.department else None,
            'team':                   user.team.team_name if user.team else None,
            'period':                 cls._period_label(period_start, period_end),
            'kpis_assigned':          assignments_qs.count(),
            'kpis_submitted':         results_qs.count(),
            'submission_rate':        cls._submission_rate(
                                          results_qs.count(), assignments_qs.count()
                                      ),
            'rating_breakdown':       cls._build_rating_breakdown(results_qs),
            'recent_results':         cls._build_recent_results(results_qs, limit=5),
            'performance_summaries':  [
                {
                    'period':         f"{s.period_start} to {s.period_end}",
                    'weighted_score': str(s.weighted_score),
                }
                for s in summaries[:3]
            ],
            'unread_notifications':   unread_notifications,
        }

    #  BUILDING BLOCKS

    @staticmethod
    def _build_overview(results_qs, assignments_qs):
        """
        High-level numbers: total KPIs, submission rate,
        average score, and rating distribution.
        """
        total_assigned  = assignments_qs.count()
        total_submitted = results_qs.count()
        avg_score       = results_qs.aggregate(
                              avg=Avg('calculated_score')
                          )['avg']

        return {
            'total_kpis_assigned':     total_assigned,
            'total_results_submitted': total_submitted,
            'submission_rate':         DashboardService._submission_rate(
                                           total_submitted, total_assigned
                                       ),
            'average_score':           round(float(avg_score), 2) if avg_score else 0,
            'rating_breakdown':        DashboardService._build_rating_breakdown(results_qs),
        }

    @staticmethod
    def _build_rating_breakdown(results_qs):
        """Count of results per rating label."""
        counts    = results_qs.values('rating').annotate(count=Count('rating'))
        breakdown = {r: 0 for r in RATING_ORDER}
        for row in counts:
            if row['rating'] in breakdown:
                breakdown[row['rating']] = row['count']
        return breakdown

    @classmethod
    def _build_department_breakdown(cls, departments, period_start, period_end):
        """
        Per-department score calculated live from approved results.
        Covers three result sources:
          1. Individual assignments to employees in this department
          2. Team assignments to teams in this department
          3. Direct department assignments
        This matches how professional HCM systems like SAP and Oracle work —
        dashboard always shows live data, not waiting for summaries.
        """
        result = []
        for dept in departments:
            # Collect all approved results belonging to this department
            dept_results = cls._filter_results(period_start, period_end).filter(
                Q(submitted_by__department=dept) |
                Q(kpi_assignment__assigned_team__department=dept) |
                Q(kpi_assignment__assigned_department=dept)
            ).distinct()

            score     = cls._average_score(dept_results)
            teams     = Team.objects.filter(department=dept)
            team_data = cls._build_team_breakdown(teams, period_start, period_end)

            result.append({
                'department_uuid': str(dept.uuid),
                'name':            dept.name,
                'weighted_score':  score,
                'rating':          cls._score_to_rating(score),
                'teams':           team_data,
            })

        return sorted(result, key=lambda d: d['weighted_score'] or 0, reverse=True)

    @classmethod
    def _build_team_breakdown(cls, teams, period_start, period_end):
        """
        Per-team score calculated live from approved results.
        Covers two result sources:
          1. Individual assignments to employees in this team
          2. Direct team assignments to this team
        """
        result = []
        for team in teams:
            # Collect all approved results belonging to this team
            team_results = cls._filter_results(period_start, period_end).filter(
                Q(submitted_by__team=team) |
                Q(kpi_assignment__assigned_team=team)
            ).distinct()

            score = cls._average_score(team_results)

            result.append({
                'team_uuid':      str(team.uuid),
                'name':           team.team_name,
                'weighted_score': score,
                'rating':         cls._score_to_rating(score),
            })

        return sorted(result, key=lambda t: t['weighted_score'] or 0, reverse=True)

    @staticmethod
    def _average_score(results_qs):
        """
        Calculate weighted average score from a queryset of results.
        Each result score is multiplied by its KPI weight so higher
        weight KPIs contribute more to the final score.
        """
        qs = results_qs.select_related('kpi_assignment__kpi')
        if not qs.exists():
            return None
        total_weighted = sum(
            float(r.calculated_score) * float(r.kpi_assignment.kpi.weight_value or 1)
            for r in qs
        )
        total_weights = sum(
            float(r.kpi_assignment.kpi.weight_value or 1)
            for r in qs
        )
        return round(total_weighted / total_weights, 1) if total_weights else None

    @staticmethod
    def _build_alerts_summary(alerts_qs):
        """Count of active and resolved alerts, broken down by type."""
        total_active     = alerts_qs.filter(is_resolved=False).count()
        underperformance = alerts_qs.filter(
                               is_resolved=False,
                               alert_type='underperformance'
                           ).count()

        dept_uuids = alerts_qs.filter(
            is_resolved=False,
            alert_type='underperformance',
            notified_department__isnull=False,
        ).values_list(
            'notified_department__name', flat=True
        ).distinct()

        return {
            'total_active_alerts':               total_active,
            'underperformance_alerts':           underperformance,
            'departments_with_underperformance': list(dept_uuids),
        }

    @staticmethod
    def _build_top_performers(results_qs, limit=5):
        """
        Users with the highest average calculated score.
        Only includes individual user submissions.
        """
        top = (
            results_qs
            .filter(submitted_by__isnull=False)
            .values(
                'submitted_by__uuid',
                'submitted_by__username',
                'submitted_by__department__name',
            )
            .annotate(avg_score=Avg('calculated_score'))
            .order_by('-avg_score')[:limit]
        )

        return [
            {
                'user_uuid':  str(row['submitted_by__uuid']),
                'username':   row['submitted_by__username'],
                'department': row['submitted_by__department__name'],
                'avg_score':  round(float(row['avg_score']), 2),
                'rating':     DashboardService._score_to_rating(
                                  float(row['avg_score'])
                              ),
            }
            for row in top
        ]

    @staticmethod
    def _build_needs_attention(results_qs, limit=5):
        """
        Users with the lowest average calculated score
        who have at least one poor or needs_improvement result.
        """
        bottom = (
            results_qs
            .filter(
                submitted_by__isnull=False,
                rating__in=['poor', 'needs_improvement'],
            )
            .values(
                'submitted_by__uuid',
                'submitted_by__username',
                'submitted_by__department__name',
            )
            .annotate(avg_score=Avg('calculated_score'))
            .order_by('avg_score')[:limit]
        )

        return [
            {
                'user_uuid':  str(row['submitted_by__uuid']),
                'username':   row['submitted_by__username'],
                'department': row['submitted_by__department__name'],
                'avg_score':  round(float(row['avg_score']), 2),
                'rating':     DashboardService._score_to_rating(
                                  float(row['avg_score'])
                              ),
            }
            for row in bottom
        ]

    @staticmethod
    def _build_recent_results(results_qs, limit=5):
        """Most recent KPI results for the employee dashboard."""
        recent = results_qs.select_related(
            'kpi_assignment__kpi'
        ).order_by('-created_at')[:limit]

        return [
            {
                'kpi_name':         r.kpi_assignment.kpi.kpi_name,
                'actual_value':     str(r.actual_value),
                'calculated_score': str(r.calculated_score),
                'rating':           r.rating,
                'submitted_at':     str(r.created_at),
            }
            for r in recent
        ]

    @staticmethod
    def _filter_results(period_start, period_end):
        # Only count approved results that are not soft deleted
        qs = KPIResults.objects.filter(
            calculated_score__isnull=False,
            is_deleted=False,
            approval_status='approved'
        )
        if period_start:
            qs = qs.filter(created_at__date__gte=period_start)
        if period_end:
            qs = qs.filter(created_at__date__lte=period_end)
        return qs

    @staticmethod
    def _filter_assignments(period_start, period_end):
        qs = KpiAssignment.objects.all()
        if period_start:
            qs = qs.filter(period_end__gte=period_start)
        if period_end:
            qs = qs.filter(period_start__lte=period_end)
        return qs

    @staticmethod
    def _submission_rate(submitted, assigned):
        if not assigned:
            return '0%'
        rate = round((submitted / assigned) * 100, 1)
        return f'{rate}%'

    @staticmethod
    def _score_to_rating(score):
        """Derive a rating label from a numeric score."""
        if score is None:
            return None
        if score >= 90: return 'outstanding'
        if score >= 75: return 'good'
        if score >= 60: return 'satisfactory'
        if score >= 40: return 'needs_improvement'
        return 'poor'

    @staticmethod
    def _period_label(period_start, period_end):
        if period_start and period_end:
            return f'{period_start} to {period_end}'
        if period_start:
            return f'From {period_start}'
        if period_end:
            return f'Up to {period_end}'
        return 'All time'