from django.db import models
from django.utils import timezone
from accounts.models import User

class TransactionLog(models.Model):
    transaction_id = models.AutoField(primary_key=True)
    transaction_name = models.CharField(max_length=100)
    table_name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action_type = models.CharField(max_length=100)
    timestamp = models.DateTimeField(default=timezone.now)
    old_value = models.FloatField(null=True, blank=True)
    new_value = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.action_type} on {self.transaction_name} id:{self.transaction_id}"






# Create your models here.
