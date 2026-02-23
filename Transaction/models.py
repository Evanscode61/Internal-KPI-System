
import uuid
from datetime import timezone, datetime
from django.utils import timezone
from django.db import models
from django.conf import settings

class TransactionLog(models.Model):
    """
    Stores audit logs for system actions (e.g., KPI assignments).
    Each log captures who did what, when, and related entity metadata.
    """

    # Primary key
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Event information
    event_code = models.CharField(max_length=100,null = True)  # e.g., 'kpi_assigned'
    status_code = models.CharField(max_length=10,default = "ACT", null = True)  # e.g., 'ACT', 'SUC', 'ERR'
    message = models.TextField(default = " This is the transaction history of this event")  # Human-readable description

    # Actor
    triggered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="transaction_logs"
    )

    # Entity being affected
    entity_type = models.CharField(max_length=100, null=True, blank=True)
    entity_uuid = models.UUIDField(null=True, blank=True)

    # Extra context
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    metadata = models.JSONField(null=True, blank=True)

    # Timestamp
    created_at = models.DateTimeField(default= timezone.now)

    class Meta:
        db_table = "transaction_logs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["event_code"]),
            models.Index(fields=["entity_uuid"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.event_code} ({self.status_code}) by {self.triggered_by}"


class EventTypes(models.Model):
    """
    Stores all possible event types for audit logging.
    Each event has a unique code and optional description.
    """

    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    code = models.CharField(
        max_length=50, unique=True,
        help_text="Unique code identifying the event, e.g., 'kpi_assigned'"
    )
    name = models.CharField(
        max_length=100,
        help_text="Human-readable name for the event"
    )
    description = models.TextField(
        blank=True, null=True,
        help_text="Optional detailed description of the event"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Flag to enable/disable this event type"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the event type was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the event type was last updated"
    )

    class Meta:
        db_table = "event_types"
        verbose_name = "Event Type"
        verbose_name_plural = "Event Types"
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} - {self.name}"






# Create your models here.
