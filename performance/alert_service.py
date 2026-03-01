from django.contrib.auth import get_user_model
from performance.models import KPIAlert, Notification
from performance.email_service import EmailNotificationService

User = get_user_model()


class AlertService:
    """
    Checks a KPI result after it is saved and creates a KPIAlert
    if the rating warrants one. Then routes email notifications to
    the correct recipients based on the assignment type.

    Rules:
        Individual assignment → notify the employee
                                notify manager if underperformance
        Team assignment       → notify the team member who submitted
                                notify manager if underperformance
        Department assignment → notify the department line manager
    """

    ALERT_TYPE_MAP = {
        'poor':              'underperformance',
        'needs_improvement': 'underperformance',
        'satisfactory':      'Average performance',
        'good':               'Improved performance',
        'outstanding':       'excellent',
    }

    @classmethod
    def check_and_create_alert(cls, result):
        """
        Entry point. Called after every KPI result is saved.
        Determines alert type from rating, creates the alert,
        then routes notifications based on assignment type.
        """
        alert_type = cls.ALERT_TYPE_MAP.get(result.rating)
        if not alert_type:
            return None
        # Check for genuine improvement — only fire if previous result was underperformance
        if alert_type == 'Improved performance':
            from kpis.models import KPIResults
            previous_result = (
                KPIResults.objects
                .filter(kpi_assignment=result.kpi_assignment)
                .exclude(uuid=result.uuid)
                .order_by('-created_at')
                .first()
            )
            if not previous_result or previous_result.rating not in ['poor', 'needs_improvement']:
                return None


        assignment = result.kpi_assignment
        score      = float(result.calculated_score) if result.calculated_score else 0
        submitter  = result.submitted_by

        # Build the alert message
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
        default_status = Status.objects.filter(code ='ACT').first()

        alert = KPIAlert.objects.create(
            kpi_assignment      = assignment,
            alert_type          = alert_type,
            threshold           = score,
            message             = message,
            notified_user       = assignment.assigned_to,
            notified_team       = assignment.assigned_team,
            notified_department = assignment.assigned_department,
            status              =default_status
        )

        # Route to the correct notification handler
        if assignment.assigned_to:
            cls._handle_individual_alert(alert, assignment.assigned_to)

        elif assignment.assigned_team:
            cls._handle_team_alert(alert, submitter)

        elif assignment.assigned_department:
            cls._handle_department_alert(alert)

        return alert

    # ── INDIVIDUAL ASSIGNMENT ─────────────────────────────────────────────────

    @classmethod
    def _handle_individual_alert(cls, alert, user):
        """
        Notify the individual user their result has been rated.
        If underperformance, also notify their line manager.
        """
        # Notify the employee — save notification first, email second
        cls._create_notification(alert, user)
        try:
            EmailNotificationService.send_kpi_alert_email(
                recipient_email = user.email,
                recipient_name  = user.username,
                alert           = alert,
            )
        except Exception as e:
            print(f'[Email ERROR] alert email to {user.email}: {e}')

        # Notify manager if underperformance
        if alert.alert_type == 'underperformance':
            cls._notify_line_manager(
                alert        = alert,
                subject_name = user.username,
                department   = user.department,
            )

    # ── TEAM ASSIGNMENT ───────────────────────────────────────────────────────

    @classmethod
    def _handle_team_alert(cls, alert, submitter):
        """
        Notify the individual team member who submitted the result.
        If underperformance, also notify the line manager.
        """
        if not submitter:
            return

        # Notify the team member who submitted
        cls._create_notification(alert, submitter)
        EmailNotificationService.send_kpi_alert_email(
            recipient_email = submitter.email,
            recipient_name  = submitter.username,
            alert           = alert,
        )

        # Notify manager if underperformance
        if alert.alert_type == 'underperformance':
            team       = alert.notified_team
            department = team.department if team else None
            cls._notify_line_manager(
                alert        = alert,
                subject_name = submitter.username,
                department   = department,
            )

    # ── DEPARTMENT ASSIGNMENT ─────────────────────────────────────────────────

    @classmethod
    def _handle_department_alert(cls, alert):
        """
        For department assignments notify the line manager directly.
        The line manager is responsible for the whole department's KPI.
        """
        department = alert.notified_department
        if not department:
            return

        cls._notify_line_manager(
            alert        = alert,
            subject_name = department.name,
            department   = department,
        )

    # ── SHARED HELPERS ────────────────────────────────────────────────────────

    @staticmethod
    def _notify_line_manager(alert, subject_name, department):
        """
        Find all line managers in the given department and
        send each one an email and an in-app notification.
        """
        if not department:
            return

        managers = User.objects.filter(
            department = department,
            role__name__in = ['Business_Line_Manager', 'Tech_Line_Manager']
        ).select_related('role')

        for manager in managers:
            AlertService._create_notification(alert, manager)
            EmailNotificationService.send_manager_alert_email(
                manager_email = manager.email,
                manager_name  = manager.username,
                alert         = alert,
                subject_name  = subject_name,
            )

    @staticmethod
    def _create_notification(alert, recipient):
        """
        Save an in-app notification record for the recipient.
        This is what users see when they call the
        GET /notifications/ endpoint.
        """
        Notification.objects.create(
            recipient         = recipient,
            alert             = alert,
            notification_type = Notification.NotificationType.KPI_ALERT,
            message           = alert.message,
            is_read           = False,
        )