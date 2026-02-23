from django.db import models
from django.contrib.auth.models import AbstractUser
from Base.models import BaseModel,Status
from organization.models import Department, Team


class User(AbstractUser):
    role = models.ForeignKey('Role', on_delete=models.SET_NULL, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True)
    phone_number = models.CharField(max_length=11, blank=True)
    status = models.ForeignKey(Status, on_delete=models.SET_NULL, null=True, blank=True)


    class Meta:
        db_table = 'users'

    def __str__(self):
        return f"{self.username} ({self.role.name if self.role else 'No Role'})"

    def is_manager_or_admin(self):
        return self.role in (self.role.MANAGER, self.role.ADMIN)

class Role(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    permissions = models.JSONField(
        blank=True,
        null=True,
        help_text="List of permission keys, e.g., ['create_kpi', 'approve_result']"
    )

    def __str__(self):
        return self.name






# Create your models here.
