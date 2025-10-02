from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Prefetch
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.models import Role, user_has_role
from apps.accounts.permissions import IsAdminOrAccountant

from .filters import AccountFilterSet, JournalEntryFilterSet
from .models import Account, JournalEntry, JournalLine
from .serializers import AccountSerializer, JournalEntrySerializer

User = get_user_model()


class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.select_related("parent").all()
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated, IsAdminOrAccountant]
    filterset_class = AccountFilterSet
    search_fields = ["code", "name"]
    ordering_fields = ["code", "name", "type"]


class JournalEntryViewSet(viewsets.ModelViewSet):
    serializer_class = JournalEntrySerializer
    permission_classes = [IsAuthenticated, IsAdminOrAccountant]
    filterset_class = JournalEntryFilterSet
    search_fields = ["memo"]
    ordering_fields = ["date", "status", "created_at"]

    def get_queryset(self):
        return (
            JournalEntry.objects.select_related("created_by", "approved_by")
            .prefetch_related(
                Prefetch(
                    "lines",
                    queryset=JournalLine.objects.select_related("account"),
                )
            )
            .all()
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        prev_status = serializer.instance.status
        entry = serializer.save()
        if prev_status != JournalEntry.Status.POSTED and entry.status == JournalEntry.Status.POSTED:
            if not user_has_role(self.request.user, Role.Code.ADMIN, Role.Code.ACCOUNTANT):
                raise PermissionDenied("Only Admin or Accountant roles can post entries.")
            if entry.approved_by is None:
                entry.approved_by = self.request.user
                entry.save(update_fields=["approved_by", "updated_at"])
        return entry

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsAdminOrAccountant])
    def post_entry(self, request, pk=None):
        entry = self.get_object()
        serializer = self.get_serializer(entry, data={"status": JournalEntry.Status.POSTED}, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)
