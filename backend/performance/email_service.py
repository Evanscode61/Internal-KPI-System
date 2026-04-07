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
            f'Weighted Score : {float(summary.weighted_score):.2f}%\n'
            f'Rating        : {summary.rating.replace("_", " ").title() if summary.rating else "N/A"}\n\n'
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
                f'Team Weighted Score : {float(summary.weighted_score):.2f}%\n'
                f'Rating             : {summary.rating.replace("_", " ").title() if summary.rating else "N/A"}\n\n'
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
            f'Weighted Score : {float(summary.weighted_score):.2f}%\n'
            f'Rating        : {summary.rating.replace("_", " ").title() if summary.rating else "N/A"}\n\n'
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
        """Notify all HR users by email every time any performance summary is generated."""
        summary_type = summary.summary_type

        if summary_type == 'individual':
            subject_name = summary.user.username if summary.user else 'Unknown'
        elif summary_type == 'team':
            subject_name = summary.team.team_name if summary.team else 'Unknown'
        else:
            subject_name = summary.department.name if summary.department else 'Unknown'

        rating  = summary.rating.replace('_', ' ').title() if summary.rating else 'N/A'
        subject = f'Performance Summary — {subject_name} ({summary_type.title()})'

        hr_users = User.objects.filter(role__name__iexact='hr')
        for hr_user in hr_users:
            message = (
                f'Dear {hr_user.username},\n\n'
                f'A new performance summary has been generated.\n\n'
                f'Summary Type  : {summary_type.title()}\n'
                f'Subject       : {subject_name}\n'
                f'Period        : {summary.period_start} to {summary.period_end}\n'
                f'Weighted Score: {float(summary.weighted_score):.2f}%\n'
                f'Rating        : {rating}\n\n'
                f'Please log in to the KPI system to review the full summary.\n\n'
                f'This is an automated message from the Internal KPI System.'
            )
            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[hr_user.email],
                    fail_silently=False,
                )
            except Exception as e:
                print(f'[Email ERROR] Could not send summary to HR user {hr_user.email}: {e}')

    @staticmethod
    def send_hr_unit_underperformance_email(hr_email, hr_name, unit_name, unit_type, avg_score):
        """Notify an individual HR user by email when a team or department
        average score drops below the satisfactory threshold."""
        subject = f'Performance Alert — {unit_type.title()} Underperformance Detected: {unit_name}'
        message = (
            f'Dear {hr_name},\n\n'
            f'This is an automated performance alert from the Internal KPI System.\n\n'
            f'A {unit_type} underperformance has been detected:\n\n'
            f'  {unit_type.title()}    : {unit_name}\n'
            f'  Average Score : {avg_score}%\n'
            f'  Status        : Below Satisfactory Threshold (60%)\n\n'
            f'This may indicate leadership, resource or structural issues '
            f'that require HR attention.\n\n'
            f'Recommended Actions:\n'
            f'  - Review individual results within this {unit_type}\n'
            f'  - Consider initiating a performance improvement plan\n'
            f'  - Consult with the line manager\n\n'
            f'Please log in to the KPI system to review the full details.\n\n'
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
            print(f'[Email ERROR] HR unit underperformance email to {hr_email}: {e}')

    # ── APPROVAL / REJECTION EMAILS ───────────────────────────────────────────

    @staticmethod
    def send_result_approved_email(employee, kpi_name, score, rating):
        """Notify employee that their KPI result has been approved."""
        subject = f'KPI Result Approved — {kpi_name}'
        message = (
            f'Dear {employee.username},\n\n'
            f'Your KPI result has been reviewed and approved by your manager.\n\n'
            f'KPI    : {kpi_name}\n'
            f'Score  : {score}%\n'
            f'Rating : {rating.replace("_", " ").title()}\n\n'
            f'Please log in to the KPI system to view your result.\n\n'
            f'This is an automated message from the Internal KPI System.'
        )
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[employee.email],
                fail_silently=False,
            )
        except Exception as e:
            print(f'[Email ERROR] Could not send approval email to {employee.email}: {e}')

    @staticmethod
    def send_result_rejected_email(employee, kpi_name, manager_comment):
        """Notify employee that their KPI result has been rejected."""
        subject = f'KPI Result Rejected — {kpi_name}'
        message = (
            f'Dear {employee.username},\n\n'
            f'Your KPI result has been reviewed and rejected by your manager.\n\n'
            f'KPI    : {kpi_name}\n'
            f'{("Manager Comment : " + manager_comment + chr(10)) if manager_comment else ""}\n'
            f'Please log in to the KPI system, correct your submission and resubmit.\n\n'
            f'This is an automated message from the Internal KPI System.'
        )
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[employee.email],
                fail_silently=False,
            )
        except Exception as e:
            print(f'[Email ERROR] Could not send rejection email to {employee.email}: {e}')

    # ── NEW ASSIGNMENT EMAIL ──────────────────────────────────────────────────

    @staticmethod
    def send_new_assignment_email(employee, kpi_name, period_start, period_end):
        """Notify employee that a new KPI has been assigned to them."""
        subject = f'New KPI Assigned — {kpi_name}'
        message = (
            f'Dear {employee.username},\n\n'
            f'A new KPI has been assigned to you.\n\n'
            f'KPI          : {kpi_name}\n'
            f'Period Start : {period_start}\n'
            f'Period End   : {period_end or "—"}\n\n'
            f'Please log in to the KPI system to view your assignment and submit your result.\n\n'
            f'This is an automated message from the Internal KPI System.'
        )
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[employee.email],
                fail_silently=False,
            )
        except Exception as e:
            print(f'[Email ERROR] Could not send assignment email to {employee.email}: {e}')