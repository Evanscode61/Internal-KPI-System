from django.db import models
from Base.models import BaseModel
from django.utils import timezone

class PerformanceSummary(BaseModel):
    user_result = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='user_result')
    department_result = models.ForeignKey('organization.Department', on_delete=models.CASCADE, related_name='department_result')
    team_result = models.ForeignKey('organization.team', on_delete=models.CASCADE, related_name='team_result')
    period_start = models.DateField()
    period_end = models.DateField()
    weighted_score = models.DecimalField(max_digits=10, decimal_places=2, default=0)


    class Meta:
        db_table = 'performance_summaries'

    def __str__(self):
        return f"{self.user_result.username} {self.period_start}–{self.period_end}: {self.weighted_score}"




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

    def __str__(self):
        return f"{self.alert_type} alert for {self.kpi_assignment}"



# Create your models here