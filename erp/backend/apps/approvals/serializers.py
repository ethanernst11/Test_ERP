from __future__ import annotations

from rest_framework import serializers

from .models import Approval, CloseChecklistItem


class ApprovalSerializer(serializers.ModelSerializer):
    actor_username = serializers.CharField(source="actor.username", read_only=True)

    class Meta:
        model = Approval
        fields = [
            "id",
            "object_type",
            "object_id",
            "status",
            "actor",
            "actor_username",
            "notes",
            "timestamp",
        ]
        read_only_fields = ["id", "actor", "actor_username", "timestamp"]


class CloseChecklistItemSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source="owner.username", read_only=True)

    class Meta:
        model = CloseChecklistItem
        fields = [
            "id",
            "name",
            "period",
            "status",
            "owner",
            "owner_username",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "owner", "owner_username", "created_at", "updated_at"]
