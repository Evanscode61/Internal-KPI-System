import uuid
from django.utils import timezone
from django.db import models
from django.conf import settings

from Base.models import Status


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


class TransactionLog(models.Model):
    """
    Stores audit logs for system actions (e.g., KPI assignments).
    Each log captures who did what, when, and related entity metadata.
    """

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # replaced plain event_code CharField with a proper FK to EventTypes.
    # This gives you referential integrity, queryable relationships, and the ability
    # to enrich event type data (description, is_active) without touching log records.
    event_type = models.ForeignKey(
        EventTypes,
        on_delete=models.PROTECT,   # PROTECT: don't allow deleting an EventType that has logs
        null=True,
        blank=True,
        related_name='transaction_logs',
        help_text="The type of event that triggered this log entry"
    )

    message = models.TextField(
        default="This is the transaction history of this event",
        help_text="Human-readable description of what happened"
    )

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

    # Status
    status = models.ForeignKey(Status, on_delete=models.PROTECT, null=True)

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "transaction_logs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["event_type"]),
            models.Index(fields=["entity_uuid"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        event_code = self.event_type.code if self.event_type else "unknown"
        triggered = self.triggered_by or "system"
        return f"{event_code} by {triggered} at {self.created_at}"






# Create your models here.
