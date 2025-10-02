from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class Account(models.Model):
    class Type(models.TextChoices):
        ASSET = "asset", "Asset"
        LIABILITY = "liability", "Liability"
        EQUITY = "equity", "Equity"
        REVENUE = "revenue", "Revenue"
        EXPENSE = "expense", "Expense"

    code = models.CharField(max_length=16, unique=True)
    name = models.CharField(max_length=128)
    type = models.CharField(max_length=16, choices=Type.choices)
    is_active = models.BooleanField(default=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        related_name="children",
        null=True,
        blank=True,
    )
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["code"]

    def __str__(self) -> str:
        return f"{self.code} – {self.name}"


class JournalEntry(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        POSTED = "posted", "Posted"

    date = models.DateField()
    memo = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="journal_entries_created",
        on_delete=models.PROTECT,
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="journal_entries_approved",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "-id"]

    def __str__(self) -> str:
        return f"JournalEntry #{self.pk} ({self.date})"

    @property
    def total_debits(self) -> Decimal:
        return self.lines.aggregate(total=models.Sum("debit"))["total"] or Decimal("0")

    @property
    def total_credits(self) -> Decimal:
        return self.lines.aggregate(total=models.Sum("credit"))["total"] or Decimal("0")


class JournalLine(models.Model):
    entry = models.ForeignKey(
        JournalEntry,
        related_name="lines",
        on_delete=models.CASCADE,
    )
    account = models.ForeignKey(Account, related_name="journal_lines", on_delete=models.PROTECT)
    debit = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    credit = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    dimensions = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["id"]

    def clean(self):
        super().clean()
        if self.debit and self.credit:
            raise ValidationError("A journal line cannot have both debit and credit values.")
        if not self.debit and not self.credit:
            raise ValidationError("A journal line must have a debit or credit value.")

    def __str__(self) -> str:
        side = "Dr" if self.debit else "Cr"
        amount = self.debit or self.credit
        return f"{self.account.code} {side} {amount}"
