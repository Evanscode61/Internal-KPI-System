from django.contrib.auth import get_user_model
from performance.models import KPIAlert, Notification
from performance.email_service import EmailNotificationService

User = get_user_model()


class AlertService:
    """
    Checks a KPI result after it is approved and creates a KPIAlert
    only for underperformance ratings. For all other ratings an
    informational notification is sent directly to the employee.

    Alert routing by assignment type:
        Individual  — employee notified, manager notified
        Team        — submitting member notified, manager notified
        Department  — submitting member notified, manager notified
    """

    # Only these ratings create an alert requiring manager action
    ALERT_RATINGS = {'poor', 'needs_improvement'}

    @classmethod
    def check_and_create_alert(cls, result):
        """
        Entry point. Called after every KPI result is approved.
        Underperformance ratings create an alert and notify both
        the employee and manager. All other ratings send an
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
            f'{subject_name} scored {score} on '
            f"'{assignment.kpi.kpi_name}' — rated {result.rating}."
        )

        # Create the alert record in the database
        from Base.models import Status
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

        # Route to the correct notification handler
        if assignment.assigned_to:
            cls._handle_individual_alert(alert, assignment.assigned_to)
        elif assignment.assigned_team:
            cls._handle_team_alert(alert, submitter)
        elif assignment.assigned_department:
            cls._handle_department_alert(alert, submitter)

        return alert

    # ── INDIVIDUAL ASSIGNMENT ─────────────────────────────────────────────────

    @classmethod
    def _handle_individual_alert(cls, alert, user):
        """
        Notify the employee their result is underperformance.
        Always notify their line manager — action is required.
        """
        # Notify the employee
        cls._create_notification(alert, user)
        try:
            EmailNotificationService.send_kpi_alert_email(
                recipient_email = user.email,
                recipient_name  = user.username,
                alert           = alert,
            )
        except Exception as e:
            print(f'[Email ERROR] alert email to {user.email}: {e}')

        # Always notify manager — underperformance always requires action
        cls._notify_line_manager(
            alert        = alert,
            subject_name = user.username,
            department   = user.department,
        )

    # ── TEAM ASSIGNMENT ───────────────────────────────────────────────────────

    @classmethod
    def _handle_team_alert(cls, alert, submitter):
        """
        Notify the team member who submitted their result is underperformance.
        Always notify their line manager — action is required.
        """
        if not submitter:
            return

        # Notify the team member who submitted
        cls._create_notification(alert, submitter)
        try:
            EmailNotificationService.send_kpi_alert_email(
                recipient_email = submitter.email,
                recipient_name  = submitter.username,
                alert           = alert,
            )
        except Exception as e:
            print(f'[Email ERROR] alert email to {submitter.email}: {e}')

        # Always notify manager — underperformance always requires action
        team       = alert.notified_team
        department = team.department if team else None
        cls._notify_line_manager(
            alert        = alert,
            subject_name = submitter.username,
            department   = department,
        )

    # ── DEPARTMENT ASSIGNMENT ─────────────────────────────────────────────────

    @classmethod
    def _handle_department_alert(cls, alert, submitter):
        """
        Notify the employee who submitted their result is underperformance.
        Always notify the line manager — action is required.
        """
        department = alert.notified_department
        if not department:
            return

        # Notify the employee who submitted
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

        # Always notify manager — underperformance always requires action
        cls._notify_line_manager(
            alert        = alert,
            subject_name = submitter.username if submitter else department.name,
            department   = department,
        )

    # ── SHARED HELPERS ────────────────────────────────────────────────────────

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

        # Notify HR , visibility of underperformance
        try:
            hr_users = User.objects.filter(role__name__iexact='hr')
            for hr_user in hr_users:
                AlertService._create_notification(alert, hr_user)
        except Exception as e:
            print(f'[Notification ERROR] HR alert notification: {e}')

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
                message           = (
                    f'Your result for "{assignment.kpi.kpi_name}" '
                    f'has been approved. Score: {score}% — Rated {label}.'
                ),
                is_read = False,
            )
        except Exception as e:
            print(f'[Notification ERROR] {e}')