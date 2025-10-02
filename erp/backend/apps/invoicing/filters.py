from __future__ import annotations

import django_filters

from .models import Invoice


class InvoiceFilterSet(django_filters.FilterSet):
    issue_date = django_filters.DateFromToRangeFilter()
    due_date = django_filters.DateFromToRangeFilter()
    status = django_filters.CharFilter()
    customer = django_filters.NumberFilter(field_name="customer_id")

    class Meta:
        model = Invoice
        fields = ["status", "customer", "issue_date", "due_date"]
