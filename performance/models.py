from django.db import models
from Base.models import BaseModel, Status
from django.contrib.auth import get_user_model

User = get_user_model()


class PerformanceSummary(BaseModel):

    class SummaryType(models.TextChoices):
        INDIVIDUAL = 'individual', 'Individual'
        TEAM       = 'team',       'Team'
        DEPARTMENT = 'department', 'Department'

    summary_type = models.CharField(
        max_length=20,
        choices=SummaryType.choices,
        default=SummaryType.INDIVIDUAL
    )

    # null=True because team/department summaries have no single user
    user       = models.ForeignKey(User, on_delete=models.CASCADE,
                     related_name='performance_summaries',
                     null=True, blank=True)
    department = models.ForeignKey('organization.Department', on_delete=models.CASCADE,
                     related_name='performance_summaries',
                     null=True, blank=True)
    team       = models.ForeignKey('organization.Team', on_delete=models.SET_NULL,
                     null=True, blank=True,
                     related_name='performance_summaries')
    period_start   = models.DateField()
    period_end     = models.DateField()
    weighted_score = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    rating = models.CharField(max_length=20, blank=True, default='')
    status         = models.ForeignKey(Status, on_delete=models.SET_NULL,
                         null=True, blank=True)

    class Meta:
        db_table = 'performance_summaries'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'period_start', 'period_end'],
                condition=models.Q(summary_type='individual'),
                name='unique_individual_summary'
            ),
            models.UniqueConstraint(
                fields=['team', 'period_start', 'period_end'],
                condition=models.Q(summary_type='team'),
                name='unique_team_summary'
            ),
            models.UniqueConstraint(
                fields=['department', 'period_start', 'period_end'],
                condition=models.Q(summary_type='department'),
                name='unique_department_summary'
            ),
        ]

    def __str__(self):
        if self.summary_type == 'individual':
            subject = self.user.username if self.user else 'Unknown'
        elif self.summary_type == 'team':
            subject = self.team.team_name if self.team else 'Unknown'
        else:
            subject = self.department.name if self.department else 'Unknown'
        return f'{subject} {self.period_start}–{self.period_end}: {self.weighted_score}'


class KPIAlert(models.Model):

    ALERT_TYPES = (
        ("underperformance", "Underperformance"),
        ("excellent", "Excellent Performance"),
        ("Average performance", "Average Performance"),
        ("Improved performance", "Improved Performance"),
    )

    kpi_assignment = models.ForeignKey('kpis.KpiAssignment',
        on_delete=models.CASCADE,
        related_name="alerts"
    )

    alert_type = models.CharField(max_length=30, choices=ALERT_TYPES)
    threshold = models.DecimalField(max_digits=6, decimal_places=2)
    message = models.TextField()

    # Optionally you can notify either a user or role
    notified_role = models.ForeignKey('accounts.Role',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="kpi_alerts"
    )

    notified_user = models.ForeignKey('accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="personal_kpi_alerts"
    )
    notified_team = models.ForeignKey('organization.Team', on_delete=models.SET_NULL, null=True, related_name="team_kpi_alerts")
    notified_department = models.ForeignKey('organization.Department', on_delete=models.SET_NULL, null=True, related_name="department_kpi_alerts")

    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    status = models.ForeignKey(Status, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.alert_type} alert for {self.kpi_assignment}"

class Notification(models.Model):

    class NotificationType(models.TextChoices):
        KPI_ALERT = 'kpi_alert', 'KPI Alert'
        SUMMARY   = 'summary',   'Performance Summary'

    recipient         = models.ForeignKey('accounts.User', on_delete=models.CASCADE,
                            related_name='notifications')
    alert             = models.ForeignKey(KPIAlert, on_delete=models.CASCADE,
                            null=True, blank=True,
                            related_name='notifications')
    summary           = models.ForeignKey(PerformanceSummary, on_delete=models.CASCADE,
                            null=True, blank=True,
                            related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NotificationType.choices)
    message           = models.TextField()
    is_read           = models.BooleanField(default=False)
    created_at        = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f'Notification for {self.recipient.username} — {self.notification_type}'

# Create your models here