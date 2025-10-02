from __future__ import annotations

import django_filters

from .models import Approval, CloseChecklistItem


class ApprovalFilterSet(django_filters.FilterSet):
    timestamp = django_filters.DateTimeFromToRangeFilter()

    class Meta:
        model = Approval
        fields = {
            "object_type": ["exact"],
            "status": ["exact"],
            "actor": ["exact"],
        }


class CloseChecklistFilterSet(django_filters.FilterSet):
    class Meta:
        model = CloseChecklistItem
        fields = {
            "period": ["exact", "icontains"],
            "status": ["exact"],
            "owner": ["exact"],
        }
