from __future__ import annotations

from rest_framework import serializers


class DateRangeSerializer(serializers.Serializer):
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)

    def validate(self, attrs):
        start = attrs.get("start_date")
        end = attrs.get("end_date")
        if start and end and start > end:
            raise serializers.ValidationError("start_date must be before end_date")
        return attrs


class IncomeStatementQuerySerializer(DateRangeSerializer):
    cadence = serializers.ChoiceField(choices=[("monthly", "Monthly"), ("quarterly", "Quarterly")], default="monthly")

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if not attrs.get("start_date") or not attrs.get("end_date"):
            raise serializers.ValidationError("start_date and end_date are required")
        return attrs


class BalanceSheetQuerySerializer(serializers.Serializer):
    as_of = serializers.DateField()


class CashFlowQuerySerializer(DateRangeSerializer):
    def validate(self, attrs):
        attrs = super().validate(attrs)
        if not attrs.get("start_date") or not attrs.get("end_date"):
            raise serializers.ValidationError("start_date and end_date are required")
        return attrs
