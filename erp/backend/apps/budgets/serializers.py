from __future__ import annotations

from rest_framework import serializers

from .models import Budget


class BudgetSerializer(serializers.ModelSerializer):
    account_code = serializers.CharField(source="account.code", read_only=True)
    account_name = serializers.CharField(source="account.name", read_only=True)

    class Meta:
        model = Budget
        fields = [
            "id",
            "account",
            "account_code",
            "account_name",
            "period_start",
            "period_end",
            "cadence",
            "amount",
            "description",
            "created_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_by", "created_at", "updated_at", "account_code", "account_name"]
