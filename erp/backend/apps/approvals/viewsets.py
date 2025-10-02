from __future__ import annotations

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import IsAdminOrAccountant, IsAdminOrReadOnly

from .filters import ApprovalFilterSet, CloseChecklistFilterSet
from .models import Approval, CloseChecklistItem
from .serializers import ApprovalSerializer, CloseChecklistItemSerializer


class ApprovalViewSet(viewsets.ModelViewSet):
    serializer_class = ApprovalSerializer
    queryset = Approval.objects.select_related("actor").all()
    permission_classes = [IsAuthenticated, IsAdminOrAccountant]
    filterset_class = ApprovalFilterSet
    ordering_fields = ["timestamp", "status", "object_type"]

    def perform_create(self, serializer):
        serializer.save(actor=self.request.user)


class CloseChecklistItemViewSet(viewsets.ModelViewSet):
    serializer_class = CloseChecklistItemSerializer
    queryset = CloseChecklistItem.objects.select_related("owner").all()
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filterset_class = CloseChecklistFilterSet
    ordering_fields = ["period", "name", "status"]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
