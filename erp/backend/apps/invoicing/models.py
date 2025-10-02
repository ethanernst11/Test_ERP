from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Customer(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    billing_address = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Invoice(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SENT = "sent", "Sent"
        PAID = "paid", "Paid"
        PARTIALLY_PAID = "partial", "Partially Paid"
        VOID = "void", "Void"

    customer = models.ForeignKey(Customer, related_name="invoices", on_delete=models.PROTECT)
    number = models.CharField(max_length=32, unique=True)
    description = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    currency = models.CharField(max_length=3, default="USD")
    issue_date = models.DateField()
    due_date = models.DateField()
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="invoices_created",
        on_delete=models.PROTECT,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-issue_date", "-id"]

    def __str__(self) -> str:
        return f"Invoice {self.number}"

    @property
    def total(self) -> Decimal:
        return self.line_items.aggregate(total=models.Sum("amount"))["total"] or Decimal("0")

    @property
    def amount_paid(self) -> Decimal:
        return self.payments.aggregate(total=models.Sum("amount"))["total"] or Decimal("0")

    @property
    def balance_due(self) -> Decimal:
        return self.total - self.amount_paid


class InvoiceLine(models.Model):
    invoice = models.ForeignKey(Invoice, related_name="line_items", on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("1.00"))
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])

    class Meta:
        ordering = ["id"]

    def save(self, *args, **kwargs):
        if not self.amount:
            self.amount = (self.unit_price or Decimal("0")) * (self.quantity or Decimal("0"))
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.description} ({self.amount})"


class Payment(models.Model):
    invoice = models.ForeignKey(Invoice, related_name="payments", on_delete=models.CASCADE)
    date = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    method = models.CharField(max_length=64, blank=True)
    reference = models.CharField(max_length=64, blank=True)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-id"]

    def __str__(self) -> str:
        return f"Payment {self.amount} on {self.date}"
