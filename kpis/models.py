from django.db import models
from Base.models import BaseModel,Status
from organization.models import Department, Team
from accounts.models import User
from django.utils import timezone
from django.conf import settings

class KpiDefinition(BaseModel):
    class Frequency(models.TextChoices):
        DAILY ='daily', 'DAILY'
        WEEKLY ='weekly', 'WEEKLY'
        MONTHLY ='monthly', 'MONTHLY'
        QUARTERLY ='quarterly', 'QUARTERLY'
        YEARLY ='yearly', 'YEARLY'
    department = models.ForeignKey(Department, on_delete=models.CASCADE,null=True,blank=True)
    kpi_name = models.CharField(max_length=255)
    frequency = models.CharField(choices=Frequency.choices, max_length=20,default=Frequency.MONTHLY)
    kpi_description = models.TextField(blank=True)
    calculation_type = models.CharField(max_length=50,null=True ,blank=True)
    weight_value = models.DecimalField(max_digits=5, decimal_places=2,default=0)
    measurement_type = models.CharField(max_length=50,help_text='% ,hours, number')
    min_threshold = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    max_threshold = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    status = models.ForeignKey(Status, on_delete=models.CASCADE,null=True)

    class Meta:
        db_table = 'kpis'
        ordering = ['-created_at']
    def __str__(self):
        return f"{self.kpi_name} ({self.department.name if self.department else 'No Department'})"

class KpiAssignment(BaseModel):
    kpi                 = models.ForeignKey(KpiDefinition, on_delete=models.CASCADE, related_name='assignments')
    assigned_department = models.ForeignKey(Department, null=True, blank=True, on_delete=models.SET_NULL, related_name='kpi_assignments')
    assigned_team       = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL, related_name='kpi_assignments')
    assigned_to         = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='kpi_assignments')
    period_start        = models.DateField(help_text='Start date', null=True, blank=True)
    period_end          = models.DateField(help_text='End date', null=True, blank=True)
    target_value        = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    weight              = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    status              = models.ForeignKey(Status, on_delete=models.SET_NULL, null=True, related_name='kpi_assignments')

    class Meta:
        db_table = 'kpisAssignments'

    def __str__(self):
        return f"{self.kpi.kpi_name} → {self.assigned_to.username if self.assigned_to else 'No User'}"

class KPIFormula(BaseModel):
    formula_name = models.CharField(max_length=30,null=True,blank=True)
    kpi = models.ForeignKey(KpiDefinition, on_delete=models.CASCADE,related_name= "formula" )
    period_start =models.DateField(help_text='Start date',null=True,blank = True)
    formula_expression = models.TextField( help_text="Example: (actual / target) * 100")
    data_source = models.CharField(
        max_length=100,blank =True,
        help_text="Example: manual_entry, jira_api,")
    status = models.ForeignKey(Status, on_delete=models.SET_NULL, null=True)
    outstanding_threshold = models.DecimalField(max_digits=5, decimal_places=2,
                                                null=True, blank=True,
                                                help_text='Score >= this = Outstanding. Default 90')
    good_threshold = models.DecimalField(max_digits=5, decimal_places=2,
                                         null=True, blank=True,
                                         help_text='Score >= this = Good. Default 75')
    satisfactory_threshold = models.DecimalField(max_digits=5, decimal_places=2,
                                                 null=True, blank=True,
                                                 help_text='Score >= this = Satisfactory. Default 60')
    needs_improvement_threshold = models.DecimalField(max_digits=5, decimal_places=2,
                                                      null=True, blank=True,
                                                      help_text='Score >= this = Needs Improvement. Default 40')
    class Meta:
        db_table = 'kpisFormula'

    def __str__(self):
        return f"Formula for {self.kpi.kpi_name if self.kpi else 'No KPI assigned'}"

class KPIResults(BaseModel):
    class Rating(models.TextChoices):
        OUTSTANDING       = 'outstanding',       'Outstanding'
        GOOD              = 'good',              'Good'
        SATISFACTORY      = 'satisfactory',      'Satisfactory'
        NEEDS_IMPROVEMENT = 'needs_improvement', 'Needs Improvement'
        POOR              = 'poor',              'Poor'

    kpi_assignment   = models.ForeignKey(KpiAssignment, on_delete=models.CASCADE,
                           related_name='results', null=True, blank=True)
    actual_value     = models.DecimalField(max_digits=10, decimal_places=4, blank=True)
    calculated_score = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    rating           = models.CharField(choices=Rating.choices, max_length=20, blank=True)
    comment          = models.TextField(blank=True)
    recorded_by      = models.ForeignKey(User, null=True, on_delete=models.SET_NULL,
                           related_name='recorded_kpi_results')
    status           = models.ForeignKey(Status, on_delete=models.CASCADE, null=True)
    submitted_by     = models.ForeignKey(User, null=True, blank=True,
                           on_delete=models.SET_NULL,
                           related_name='submitted_kpi_results',
                           help_text='The individual member submitting under a team/dept assignment')

    class ApprovalStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'

    approval_status = models.CharField(
        choices=ApprovalStatus.choices,
        max_length=20,
        default='pending'
    )
    manager_comment = models.TextField(blank=True, null=True)
    reviewed_by = models.ForeignKey(
        User, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='reviewed_kpi_results'
    )

    class Meta:
        db_table = 'kpisResults'
        constraints = [
            models.UniqueConstraint(
                fields = ['submitted_by', 'kpi_assignment'],
                name = 'unique_submitted_by_kpi_assignment',
            )
        ]








