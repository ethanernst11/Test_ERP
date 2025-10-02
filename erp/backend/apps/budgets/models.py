from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models

from apps.ledger.models import Account


class Budget(models.Model):
    class Cadence(models.TextChoices):
        MONTHLY = "monthly", "Monthly"
        QUARTERLY = "quarterly", "Quarterly"

    account = models.ForeignKey(Account, related_name="budgets", on_delete=models.CASCADE)
    period_start = models.DateField()
    period_end = models.DateField()
    cadence = models.CharField(max_length=16, choices=Cadence.choices)
    amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0"))
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="budgets_created",
        on_delete=models.PROTECT,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-period_start", "account__code"]
        unique_together = ("account", "period_start", "period_end", "cadence")

    def __str__(self) -> str:
        return f"Budget {self.account.code} {self.period_start} - {self.period_end}"
