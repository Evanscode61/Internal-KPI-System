import uuid
from django.db import models
from django.conf import settings


class BaseModel(models.Model):
    """ # UUID primary key instead of auto-increment integer
    Better for security and distributed systems"""

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4,editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name="%(class)s_created")
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name="%(class)s_updated")
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True
"""status model to be used by other models"""
class Status(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = "Statuses"

    def __str__(self):
        return self.name
# Create your models here.
