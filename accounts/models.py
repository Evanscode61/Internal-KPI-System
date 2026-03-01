from django.db import models
from django.contrib.auth.models import AbstractUser
from Base.models import BaseModel, Status
from organization.models import Department, Team
from django.conf import settings


class User(AbstractUser, BaseModel):
    role         = models.ForeignKey('Role', on_delete=models.SET_NULL, null=True, blank=True)
    department   = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    team         = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True)
    phone_number = models.CharField(max_length=11, blank=True)
    status       = models.ForeignKey(Status, on_delete=models.SET_NULL, null=True, blank=True)
    is_active    = models.BooleanField(default=True)

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f"{self.username} ({self.role.name if self.role else 'No Role'})"

    def is_manager_or_admin(self):
        return self.role in (self.role.MANAGER, self.role.ADMIN)


class Permission(BaseModel):
    """
    Represents a single action a role can perform.
    e.g. create_kpi, delete_department, generate_summary
    """
    name        = models.CharField(max_length=100, unique=True)
    codename    = models.CharField(max_length=100, unique=True,
                      help_text='Unique code used in decorators e.g. create_kpi')
    description = models.TextField(blank=True,
                      help_text='What this permission allows')

    class Meta:
        db_table = 'permissions'
        ordering = ['codename']

    def __str__(self):
        return f'{self.name} ({self.codename})'

    def has_perm(self, codename: str) -> bool:
        """
        Check if this user's role has a specific permission.
        Usage: request.user.has_perm('create_kpi')
        """
        if not self.role:
            return False
        return self.role.has_permission(codename)


class Role(BaseModel):
    name        = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active   = models.BooleanField(default=True)
    permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name='roles',
        help_text='Permissions assigned to this role'
    )
    status = models.ForeignKey(Status, on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = 'roles'

    def __str__(self):
        return self.name

    def has_permissions(self, codename: str) -> bool:
        """Check if this role has a specific permission."""
        return self.permissions.filter(codename=codename).exists()


class RefreshToken(models.Model):
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token      = models.TextField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)


# ─── OTP Model ───────────────────────────────────────────────────────────────

class OTP(models.Model):
    """
    Stores one-time passwords for password reset and first-login flows.
    Each OTP is tied to a user, has a purpose, expires after 10 minutes,
    and can only be used once.
    """

    PURPOSE_RESET       = 'password_reset'
    PURPOSE_FIRST_LOGIN = 'first_login'
    PURPOSE_CHOICES = [
        (PURPOSE_RESET,       'Password Reset'),
        (PURPOSE_FIRST_LOGIN, 'First Login'),
    ]

    user       = models.ForeignKey(
                     settings.AUTH_USER_MODEL,
                     on_delete=models.CASCADE,
                     related_name='otps'
                 )
    code       = models.CharField(max_length=6)
    purpose    = models.CharField(max_length=20, choices=PURPOSE_CHOICES, default=PURPOSE_RESET)
    is_used    = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'otps'
        ordering = ['-created_at']

    def is_valid(self):
        """Returns True if the OTP has not been used and has not expired."""
        from django.utils import timezone
        return not self.is_used and self.expires_at > timezone.now()

    def __str__(self):
        return f'OTP for {self.user.username} [{self.purpose}] — used: {self.is_used}'