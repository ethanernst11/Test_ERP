from __future__ import annotations

import django_filters

from .models import Account, JournalEntry


class AccountFilterSet(django_filters.FilterSet):
    class Meta:
        model = Account
        fields = {
            "type": ["exact"],
            "is_active": ["exact"],
            "code": ["icontains"],
            "name": ["icontains"],
        }


class JournalEntryFilterSet(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter()
    status = django_filters.CharFilter(field_name="status")
    account = django_filters.NumberFilter(field_name="lines__account", distinct=True)

    class Meta:
        model = JournalEntry
        fields = {
            "status": ["exact"],
            "created_by": ["exact"],
            "approved_by": ["exact"],
        }
