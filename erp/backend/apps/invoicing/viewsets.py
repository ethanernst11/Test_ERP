from __future__ import annotations

from django.db import transaction
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import IsAdminOrAccountant

from .filters import InvoiceFilterSet
from .models import Customer, Invoice, Payment
from .serializers import CustomerSerializer, InvoiceSerializer, PaymentSerializer


class CustomerViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerSerializer
    queryset = Customer.objects.all()
    permission_classes = [IsAuthenticated, IsAdminOrAccountant]
    search_fields = ["name", "email"]
    ordering_fields = ["name", "created_at"]


class InvoiceViewSet(viewsets.ModelViewSet):
    serializer_class = InvoiceSerializer
    queryset = Invoice.objects.select_related("customer", "created_by").prefetch_related("line_items", "payments")
    permission_classes = [IsAuthenticated, IsAdminOrAccountant]
    filterset_class = InvoiceFilterSet
    ordering_fields = ["issue_date", "due_date", "status"]
    search_fields = ["number", "customer__name", "customer__email"]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.select_related("invoice", "invoice__customer")
    permission_classes = [IsAuthenticated, IsAdminOrAccountant]
    ordering_fields = ["date", "amount"]

    def perform_create(self, serializer):
        with transaction.atomic():
            payment = serializer.save()
            self._sync_invoice(payment.invoice)

    def perform_update(self, serializer):
        with transaction.atomic():
            payment = serializer.save()
            self._sync_invoice(payment.invoice)

    def perform_destroy(self, instance):
        invoice = instance.invoice
        with transaction.atomic():
            super().perform_destroy(instance)
            self._sync_invoice(invoice)

    def _sync_invoice(self, invoice: Invoice) -> None:
        total = invoice.total
        paid = invoice.amount_paid
        if paid >= total and total > 0:
            new_status = Invoice.Status.PAID
        elif 0 < paid < total:
            new_status = Invoice.Status.PARTIALLY_PAID
        elif paid == 0 and total > 0:
            new_status = Invoice.Status.SENT
        else:
            new_status = invoice.status

        if invoice.status != new_status:
            invoice.status = new_status
            invoice.save(update_fields=["status", "updated_at"])
        else:
            invoice.save(update_fields=["updated_at"])
