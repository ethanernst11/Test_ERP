from __future__ import annotations

import django_filters

from .models import Budget


class BudgetFilterSet(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name="period_start")
    account = django_filters.NumberFilter(field_name="account")

    class Meta:
        model = Budget
        fields = {
            "cadence": ["exact"],
        }
