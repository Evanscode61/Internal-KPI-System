from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


class EmailNotificationService:
    """
    Handles all email notifications for the KPI system.
    Covers KPI alerts and performance summary notifications.
    """

    # ── KPI ALERT EMAILS ──────────────────────────────────────────────────────

    @staticmethod
    def send_kpi_alert_email(recipient_email, recipient_name, alert):
        """Send a KPI alert email to a single recipient."""
        assignment = alert.kpi_assignment
        kpi_name   = assignment.kpi.kpi_name
        score      = alert.threshold
        alert_type = alert.alert_type

        subject = f'KPI Alert: {alert_type.title()} — {kpi_name}'

        message = (
            f'Dear {recipient_name},\n\n'
            f'This is a notification regarding the KPI: {kpi_name}\n\n'
            f'Alert Type : {alert_type.upper()}\n'
            f'Score      : {score}\n'
            f'Details    : {alert.message}\n\n'
            f'Please log in to the KPI system to view the full details.\n\n'
            f'This is an automated message from the Internal KPI System.'
        )

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient_email],
                fail_silently=False,
            )
        except Exception as e:
            print(f'[Email ERROR] Could not send to {recipient_email}: {e}')

    @staticmethod
    def send_manager_alert_email(manager_email, manager_name, alert, subject_name):
        """Send an underperformance alert email specifically to a line manager."""
        kpi_name = alert.kpi_assignment.kpi.kpi_name
        score    = alert.threshold

        subject = f'[Manager Alert] Underperformance Detected — {kpi_name}'

        message = (
            f'Dear {manager_name},\n\n'
            f'An underperformance alert has been triggered in your department/team.\n\n'
            f'Employee/Team : {subject_name}\n'
            f'KPI           : {kpi_name}\n'
            f'Score         : {score}\n'
            f'Details       : {alert.message}\n\n'
            f'Please review and take necessary action.\n\n'
            f'This is an automated message from the Internal KPI System.'
        )

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[manager_email],
                fail_silently=False,
            )
        except Exception as e:
            print(f'[Email ERROR] Could not send manager alert to {manager_email}: {e}')

    # ── PERFORMANCE SUMMARY EMAILS ────────────────────────────────────────────

    @staticmethod
    def send_individual_summary_email(user, summary):
        """Notify the employee that their individual summary has been generated."""
        subject = f'Your Performance Summary is Ready — {summary.period_start} to {summary.period_end}'

        message = (
            f'Dear {user.username},\n\n'
            f'Your performance summary for the period '
            f'{summary.period_start} to {summary.period_end} has been generated.\n\n'
            f'Weighted Score : {summary.weighted_score}\n\n'
            f'Please log in to the KPI system to view your full summary.\n\n'
            f'This is an automated message from the Internal KPI System.'
        )

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
        except Exception as e:
            print(f'[Email ERROR] Could not send individual summary to {user.email}: {e}')

    @staticmethod
    def send_team_summary_email(team_members, summary):
        """Notify all team members that their team summary has been generated."""
        team_name = summary.team.team_name if summary.team else 'Your Team'
        subject   = f'Team Performance Summary Ready — {team_name} ({summary.period_start} to {summary.period_end})'

        for member in team_members:
            message = (
                f'Dear {member.username},\n\n'
                f'The performance summary for {team_name} covering '
                f'{summary.period_start} to {summary.period_end} has been generated.\n\n'
                f'Team Weighted Score : {summary.weighted_score}\n\n'
                f'Please log in to the KPI system to view the full team summary.\n\n'
                f'This is an automated message from the Internal KPI System.'
            )

            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[member.email],
                    fail_silently=False,
                )
            except Exception as e:
                print(f'[Email ERROR] Could not send team summary to {member.email}: {e}')

    @staticmethod
    def send_manager_summary_email(manager, summary):
        """Notify a line manager that a team or department summary is ready."""
        summary_type = summary.summary_type

        if summary_type == 'team':
            subject_name = summary.team.team_name if summary.team else 'Unknown Team'
        else:
            subject_name = summary.department.name if summary.department else 'Unknown Department'

        subject = f'[Manager] {summary_type.title()} Performance Summary Ready — {subject_name}'

        message = (
            f'Dear {manager.username},\n\n'
            f'The {summary_type} performance summary for {subject_name} '
            f'covering {summary.period_start} to {summary.period_end} has been generated.\n\n'
            f'Weighted Score : {summary.weighted_score}\n\n'
            f'Please log in to the KPI system to review the summary.\n\n'
            f'This is an automated message from the Internal KPI System.'
        )

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[manager.email],
                fail_silently=False,
            )
        except Exception as e:
            print(f'[Email ERROR] Could not send manager summary to {manager.email}: {e}')

    @staticmethod
    def send_summary_to_hr(summary):
        """Notify HR every time any performance summary is generated."""
        hr_email = getattr(settings, 'HR_NOTIFICATION_EMAIL', None)
        if not hr_email:
            print('[Email WARNING] HR_NOTIFICATION_EMAIL not set in settings')
            return

        summary_type = summary.summary_type

        if summary_type == 'individual':
            subject_name = summary.user.username if summary.user else 'Unknown'
        elif summary_type == 'team':
            subject_name = summary.team.team_name if summary.team else 'Unknown'
        else:
            subject_name = summary.department.name if summary.department else 'Unknown'

        subject = f'Performance Summary Generated — {subject_name} ({summary_type.title()})'

        message = (
            f'Dear HR,\n\n'
            f'A new performance summary has been generated.\n\n'
            f'Summary Type  : {summary_type.upper()}\n'
            f'Subject       : {subject_name}\n'
            f'Period        : {summary.period_start} to {summary.period_end}\n'
            f'Weighted Score: {summary.weighted_score}\n\n'
            f'Please log in to the KPI system to review the full summary.\n\n'
            f'This is an automated message from the Internal KPI System.'
        )

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[hr_email],
                fail_silently=False,
            )
        except Exception as e:
            print(f'[Email ERROR] Could not send summary to HR: {e}')