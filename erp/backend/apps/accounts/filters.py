from __future__ import annotations

import django_filters
from django.contrib.auth import get_user_model

User = get_user_model()


class UserFilterSet(django_filters.FilterSet):
    role = django_filters.CharFilter(method="filter_role")

    class Meta:
        model = User
        fields = {"is_active": ["exact"], "username": ["icontains"], "email": ["icontains"]}

    def filter_role(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(erp_roles__code=value)
