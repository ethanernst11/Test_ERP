from __future__ import annotations

from django.conf import settings
from django.db import models


class Approval(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    object_type = models.CharField(max_length=64)
    object_id = models.CharField(max_length=64)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="approvals", on_delete=models.PROTECT)
    notes = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self) -> str:
        return f"{self.object_type} {self.object_id} – {self.status}"


class CloseChecklistItem(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETE = "complete", "Complete"

    name = models.CharField(max_length=128)
    period = models.CharField(max_length=32)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="checklist_items", on_delete=models.PROTECT)
    notes = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["period", "name"]

    def __str__(self) -> str:
        return f"{self.period}: {self.name}"
