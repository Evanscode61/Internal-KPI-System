from django.contrib.auth import get_user_model
from django.db.models import Avg
from kpis.models import KPIResults
from performance.models import KPIAlert, Notification
from performance.email_service import EmailNotificationService
from Base.models import Status

User = get_user_model()


class AlertService:
    """
    Checks a KPI result after it is approved and creates a KPIAlert
    only for underperformance ratings. For all other ratings an
    informational notification is sent directly to the employee.

    Rule — same for all assignment types (individual, team, department):
        Submitter notified — in-app + email
        Line manager notified — in-app + email
        HR notified only for systemic unit underperformance
    """

    ALERT_RATINGS = {'poor', 'needs_improvement'}

    @classmethod
    def check_and_create_alert(cls, result):
        """
        Entry point. Called after every KPI result is approved.
        Underperformance ratings create an alert and notify both
        the submitter and manager. All other ratings send an
        informational notification to the employee only.
        """
        assignment = result.kpi_assignment
        score      = float(result.calculated_score) if result.calculated_score else 0
        submitter  = result.submitted_by

        # Non-underperformance — informational notification only, no alert
        if result.rating not in cls.ALERT_RATINGS:
            cls._create_performance_notification(result)
            return None

        # Build subject name for alert message
        if assignment.assigned_to:
            subject_name = assignment.assigned_to.username
        elif assignment.assigned_team:
            subject_name = assignment.assigned_team.team_name
        elif assignment.assigned_department:
            subject_name = assignment.assigned_department.name
        else:
            return None

        message = (
            f'{subject_name} scored {float(score):.2f}% on '
            f"'{assignment.kpi.kpi_name}' — rated {result.rating.replace('_', ' ').title()}."
        )

        default_status = Status.objects.filter(code='ACT').first()

        alert = KPIAlert.objects.create(
            kpi_assignment      = assignment,
            alert_type          = 'underperformance',
            threshold           = score,
            message             = message,
            notified_user       = assignment.assigned_to,
            notified_team       = assignment.assigned_team,
            notified_department = assignment.assigned_department,
            status              = default_status
        )

        # Resolve department regardless of assignment type
        if assignment.assigned_to:
            department = assignment.assigned_to.department
        elif assignment.assigned_team:
            department = assignment.assigned_team.department
        elif assignment.assigned_department:
            department = assignment.assigned_department
        else:
            department = None

        # Single handler — same rule for all assignment types
        cls._handle_underperformance_alert(alert, submitter, department)

        # Check team/department average after alert
        cls._check_unit_underperformance(result)

        return alert

    # ── SHARED HELPERS ────────────────────────────────────────────────────────

    @classmethod
    def _handle_underperformance_alert(cls, alert, submitter, department):
        """
        Single handler for all assignment types — individual, team and department.
        Rule is always the same: notify the submitter and their line manager.
        HR is not notified here — systemic underperformance is handled separately
        via _check_unit_underperformance.
        """
        # Notify the submitter
        if submitter:
            cls._create_notification(alert, submitter)
            try:
                EmailNotificationService.send_kpi_alert_email(
                    recipient_email = submitter.email,
                    recipient_name  = submitter.username,
                    alert           = alert,
                )
            except Exception as e:
                print(f'[Email ERROR] alert email to {submitter.email}: {e}')

        # Always notify line manager — action is required
        cls._notify_line_manager(
            alert        = alert,
            subject_name = submitter.username if submitter else 'Unknown',
            department   = department,
        )

    @staticmethod
    def _notify_line_manager(alert, subject_name, department):
        if not department:
            return

        managers = User.objects.filter(
            department=department,
            role__name__in=['Business_Line_Manager', 'Tech_Line_Manager']
        ).select_related('role')

        for manager in managers:
            AlertService._create_notification(alert, manager)
            try:
                EmailNotificationService.send_manager_alert_email(
                    manager_email=manager.email,
                    manager_name=manager.username,
                    alert=alert,
                    subject_name=subject_name,
                )
            except Exception as e:
                print(f'[Email ERROR] manager alert email to {manager.email}: {e}')

        # HR is notified of systemic underperformance (team/dept level)
        # via _check_unit_underperformance — not individual alerts

    @staticmethod
    def _create_notification(alert, recipient):
        """
        Save an in-app notification record for the recipient.
        This is what users see in their notifications panel.
        """
        Notification.objects.create(
            recipient         = recipient,
            alert             = alert,
            notification_type = Notification.NotificationType.KPI_ALERT,
            message           = alert.message,
            is_read           = False,
        )

    @classmethod
    def _create_performance_notification(cls, result):
        """
        For non-underperformance ratings — send a simple informational
        notification directly to the employee. No alert record created.
        No manager notification needed.
        """
        assignment = result.kpi_assignment
        submitter  = result.submitted_by
        score      = float(result.calculated_score) if result.calculated_score else 0

        if not submitter:
            return

        rating_labels = {
            'satisfactory': 'Satisfactory',
            'good':         'Good',
            'outstanding':  'Outstanding',
        }
        label = rating_labels.get(result.rating, result.rating)

        try:
            Notification.objects.create(
                recipient         = submitter,
                notification_type = Notification.NotificationType.KPI_ALERT,
                message=(
                    f'Your result for "{assignment.kpi.kpi_name}" '
                    f'has been approved. Score: {float(score):.2f}% — Rated {label}.'
                ),
                is_read = False,
            )
        except Exception as e:
            print(f'[Notification ERROR] {e}')

    @classmethod
    def _check_unit_underperformance(cls, result):
        """
        After a team or department result is approved, recalculate
        the unit average. If it drops below the satisfactory threshold
        (60%), notify HR.

        Only fires for team and department assignments — individual
        underperformance is already handled separately through the
        existing alert path which notifies the submitter and manager.

        Since every member submits their own result under the shared
        assignment, the average is recalculated each time a result is
        approved — giving HR an up-to-date picture of unit performance.
        """
        assignment = result.kpi_assignment
        THRESHOLD  = 60.0

        # ── Team assignment — check team average
        if assignment.assigned_team:
            team = assignment.assigned_team
            avg = KPIResults.objects.filter(
                kpi_assignment__assigned_team=team,
                approval_status='approved',
                is_deleted=False,
                calculated_score__isnull=False,
            ).aggregate(avg=Avg('calculated_score'))['avg']

            if avg and float(avg) < THRESHOLD:
                cls._notify_hr_unit_underperformance(
                    unit_name=team.team_name,
                    unit_type='team',
                    avg_score=round(float(avg), 1),
                )

        # ── Department assignment — check department average
        elif assignment.assigned_department:
            dept = assignment.assigned_department
            avg = KPIResults.objects.filter(
                kpi_assignment__assigned_department=dept,
                approval_status='approved',
                is_deleted=False,
                calculated_score__isnull=False,
            ).aggregate(avg=Avg('calculated_score'))['avg']

            if avg and float(avg) < THRESHOLD:
                cls._notify_hr_unit_underperformance(
                    unit_name=dept.name,
                    unit_type='department',
                    avg_score=round(float(avg), 1),
                )

    @staticmethod
    def _notify_hr_unit_underperformance(unit_name, unit_type, avg_score):
        """
        Notify all HR users — both in-app and email — when a team
        or department average score drops below the satisfactory threshold.
        """
        message = (
            f"{unit_type.title()} performance drop detected — '{unit_name}' "
            f"average score is {avg_score}% which is below the satisfactory "
            f"threshold. Consider initiating a performance review or coaching intervention."
        )

        hr_users = User.objects.filter(role__name__iexact='hr')
        for hr_user in hr_users:
            # In-app notification
            Notification.objects.create(
                recipient         = hr_user,
                notification_type = 'kpi_alert',
                message           = message,
                is_read           = False,
            )
            # Email notification
            try:
                EmailNotificationService.send_hr_unit_underperformance_email(
                    hr_email  = hr_user.email,
                    hr_name   = hr_user.username,
                    unit_name = unit_name,
                    unit_type = unit_type,
                    avg_score = avg_score,
                )
            except Exception as e:
                print(f'[Email ERROR] HR unit underperformance email to {hr_user.email}: {e}')