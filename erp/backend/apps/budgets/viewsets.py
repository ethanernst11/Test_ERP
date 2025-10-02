from __future__ import annotations

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import IsAdminOrAccountant

from .filters import BudgetFilterSet
from .models import Budget
from .serializers import BudgetSerializer


class BudgetViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetSerializer
    queryset = Budget.objects.select_related("account", "created_by").all()
    permission_classes = [IsAuthenticated, IsAdminOrAccountant]
    filterset_class = BudgetFilterSet
    ordering_fields = ["period_start", "account__code", "amount"]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
