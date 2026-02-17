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
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    frequency = models.CharField(choices=Frequency.choices, max_length=20,default=Frequency.MONTHLY)
    formula = models.ForeignKey('KPIFormula', on_delete=models.PROTECT)
    measurement_type = models.CharField(max_length=50,help_text='% ,hours, number')
    minimum_threshold = models.FloatField(default=0.0)
    maximum_threshold = models.FloatField(default=0.0)
    status = models.ForeignKey(Status, on_delete=models.CASCADE,null=True)

    class Meta:
        db_table = 'kpis'
        ordering = ['-created_at']
    def __str__(self):
        return f"{self.name} ({self.department.name})"

class KpiAssignment(BaseModel):
    kpi = models.ForeignKey(KpiDefinition, on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(Department,null= True, blank = True, on_delete=models.CASCADE)
    assigned_team = models.ForeignKey(Team,null= True, blank = True, on_delete=models.CASCADE)
    assigned_user = models.ForeignKey(User,null = True, blank =True, on_delete=models.CASCADE)
    period_start = models.DateField(help_text='Start date')
    period_end = models.DateField(help_text='End date')
    target_value = models.DecimalField(max_digits=5, decimal_places=2,default=0)
    weight = models.DecimalField(max_digits=5, decimal_places=2,help_text='Weight of the assignment')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.ForeignKey(Status, on_delete=models.CASCADE,null = True)

    class Meta:
        db_table = 'kpiAssignment'
        ordering = ['-period_start','-period_end']

    def __str__(self):
        return f"{self.kpi.name}|{self.period_start} ({self.period_end})"

class KPIFormula(BaseModel):
    formula_name = models.CharField(max_length=30,null=True,blank=True)
    kpi = models.OneToOneField(KpiDefinition,null =True ,blank = True, on_delete=models.CASCADE)
    period_start = models.DateField(help_text='Start date')
    formula_expression = models.TextField( help_text="Example: (actual / target) * 100")
    data_source = models.CharField(
        max_length=100,
        help_text="Example: manual_entry, jira_api,")

    def __str__(self):
        return f"Formula for {self.kpi.name if self.kpi else 'No KPI assigned'}"


class KPIResults(BaseModel):
    # result entered by assigned individual and calculations done by the calculation engine
    class Rating(models.TextChoices):
        OUTSTANDING = 'outstanding', 'OUTSTANDING'
        GOOD = 'good', 'GOOD'
        LOW = 'low', 'LOW'

    KpiAssignment = models.ForeignKey(KpiAssignment, on_delete=models.CASCADE)
    calculated_score = models.DecimalField(max_digits=5, decimal_places=2,blank=True)
    actual_value = models.DecimalField(max_digits=5, decimal_places=2,blank=True)
    rating =models.CharField(choices=Rating.choices, max_length=20)
    comment = models.TextField(blank=True)
    recorded_by = models.ForeignKey(User,null= True, on_delete=models.SET_NULL,related_name='recorded_kpiResults')
    status = models.ForeignKey(Status, on_delete=models.CASCADE,null=True)
    class Meta:
        db_table = 'kpisResults'

    def __str__(self):
        return f"Result for {self.KpiAssignment}"








