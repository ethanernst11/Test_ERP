from __future__ import annotations

from decimal import Decimal

from django.db import transaction
from rest_framework import serializers

from .models import Account, JournalEntry, JournalLine


class AccountSerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(source="parent.name", read_only=True)

    class Meta:
        model = Account
        fields = [
            "id",
            "code",
            "name",
            "type",
            "is_active",
            "parent",
            "parent_name",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class JournalLineSerializer(serializers.ModelSerializer):
    account_code = serializers.CharField(source="account.code", read_only=True)
    account_name = serializers.CharField(source="account.name", read_only=True)

    class Meta:
        model = JournalLine
        fields = [
            "id",
            "account",
            "account_code",
            "account_name",
            "debit",
            "credit",
            "dimensions",
        ]
        read_only_fields = ["id", "account_code", "account_name"]

    def validate(self, attrs):
        debit = attrs.get("debit") or Decimal("0")
        credit = attrs.get("credit") or Decimal("0")
        if debit and credit:
            raise serializers.ValidationError("A line cannot include both debit and credit values.")
        if not debit and not credit:
            raise serializers.ValidationError("A line requires a debit or credit value.")
        return attrs


class JournalEntrySerializer(serializers.ModelSerializer):
    lines = JournalLineSerializer(many=True, required=False)
    created_by = serializers.StringRelatedField(read_only=True)
    approved_by = serializers.StringRelatedField(read_only=True)
    total_debits = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    total_credits = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)

    class Meta:
        model = JournalEntry
        fields = [
            "id",
            "date",
            "memo",
            "status",
            "created_by",
            "approved_by",
            "lines",
            "created_at",
            "updated_at",
            "total_debits",
            "total_credits",
        ]
        read_only_fields = [
            "id",
            "created_by",
            "approved_by",
            "created_at",
            "updated_at",
            "total_debits",
            "total_credits",
        ]

    def _validate_double_entry(self, status: str, lines_data) -> None:
        if status != JournalEntry.Status.POSTED:
            return
        if not lines_data:
            raise serializers.ValidationError("Posted entries require at least one line.")

        def to_decimal(value):
            if value in (None, "", 0):
                return Decimal("0")
            return value if isinstance(value, Decimal) else Decimal(str(value))

        debit = sum(to_decimal(line.get("debit")) for line in lines_data)
        credit = sum(to_decimal(line.get("credit")) for line in lines_data)
        if debit != credit:
            raise serializers.ValidationError("Posted entries must balance debits and credits.")

    def create(self, validated_data):
        lines_data = validated_data.pop("lines", [])
        status_value = validated_data.get("status", JournalEntry.Status.DRAFT)
        self._validate_double_entry(status_value, lines_data)
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data["created_by"] = request.user
        with transaction.atomic():
            entry = JournalEntry.objects.create(**validated_data)
            self._upsert_lines(entry, lines_data)
        return entry

    def update(self, instance, validated_data):
        lines_data = validated_data.pop("lines", None)
        status_value = validated_data.get("status", instance.status)
        if lines_data is None:
            lines_data = [
                {
                    "account": line.account,
                    "debit": line.debit,
                    "credit": line.credit,
                    "dimensions": line.dimensions,
                }
                for line in instance.lines.all()
            ]
        else:
            # `account` may be ID; ensure integer not object for validation
            prepared = []
            for data in lines_data:
                prepared.append({
                    "account": data.get("account"),
                    "debit": data.get("debit"),
                    "credit": data.get("credit"),
                    "dimensions": data.get("dimensions", {}),
                })
            lines_data = prepared
        self._validate_double_entry(status_value, lines_data)
        with transaction.atomic():
            entry = super().update(instance, validated_data)
            if lines_data is not None and self.partial is False:
                entry.lines.all().delete()
                self._upsert_lines(entry, lines_data)
            elif lines_data is not None and self.partial is True:
                entry.lines.all().delete()
                self._upsert_lines(entry, lines_data)
        return entry

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["total_debits"] = f"{instance.total_debits:.2f}"
        data["total_credits"] = f"{instance.total_credits:.2f}"
        return data

    def _upsert_lines(self, entry: JournalEntry, lines_data):
        line_instances = []
        for payload in lines_data:
            account = payload["account"]
            if isinstance(account, Account):
                account_obj = account
            else:
                account_obj = Account.objects.get(pk=account)
            line_instances.append(
                JournalLine(
                    entry=entry,
                    account=account_obj,
                    debit=Decimal(str(payload.get("debit") or "0")),
                    credit=Decimal(str(payload.get("credit") or "0")),
                    dimensions=payload.get("dimensions", {}),
                )
            )
        JournalLine.objects.bulk_create(line_instances)
