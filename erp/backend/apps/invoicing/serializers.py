from __future__ import annotations

from decimal import Decimal

from rest_framework import serializers

from .models import Customer, Invoice, InvoiceLine, Payment


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ["id", "name", "email", "billing_address", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class InvoiceLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceLine
        fields = ["id", "description", "quantity", "unit_price", "amount"]
        read_only_fields = ["id", "amount"]


class PaymentSerializer(serializers.ModelSerializer):
    remaining_balance = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "invoice",
            "date",
            "amount",
            "method",
            "reference",
            "notes",
            "created_at",
            "remaining_balance",
        ]
        read_only_fields = ["id", "created_at", "remaining_balance"]

    def validate(self, attrs):
        invoice = attrs.get("invoice") or getattr(self.instance, "invoice", None)
        amount = attrs.get("amount")
        if invoice is None or amount is None:
            return attrs
        amount = amount or Decimal("0")
        if amount <= 0:
            raise serializers.ValidationError({"amount": "Amount must be greater than zero."})
        balance = invoice.balance_due
        if self.instance:
            balance += self.instance.amount
        if amount > balance:
            raise serializers.ValidationError({"amount": "Payment exceeds remaining balance."})
        attrs["remaining_balance"] = balance - amount
        return attrs

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["remaining_balance"] = str(instance.invoice.balance_due)
        return data

    def create(self, validated_data):
        validated_data.pop("remaining_balance", None)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.pop("remaining_balance", None)
        return super().update(instance, validated_data)


class InvoiceSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    customer_id = serializers.PrimaryKeyRelatedField(
        queryset=Customer.objects.all(), source="customer", write_only=True
    )
    line_items = InvoiceLineSerializer(many=True)
    payments = PaymentSerializer(many=True, read_only=True)
    total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    amount_paid = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    balance_due = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Invoice
        fields = [
            "id",
            "number",
            "description",
            "status",
            "currency",
            "issue_date",
            "due_date",
            "notes",
            "customer",
            "customer_id",
            "line_items",
            "payments",
            "total",
            "amount_paid",
            "balance_due",
            "created_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "payments",
            "total",
            "amount_paid",
            "balance_due",
            "created_by",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        line_items_data = validated_data.pop("line_items", [])
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data["created_by"] = request.user
        invoice = Invoice.objects.create(**validated_data)
        self._create_lines(invoice, line_items_data)
        return invoice

    def update(self, instance, validated_data):
        line_items_data = validated_data.pop("line_items", None)
        invoice = super().update(instance, validated_data)
        if line_items_data is not None:
            invoice.line_items.all().delete()
            self._create_lines(invoice, line_items_data)
        return invoice

    def _create_lines(self, invoice: Invoice, line_items_data):
        for line in line_items_data:
            quantity = line.get("quantity") or 1
            unit_price = line.get("unit_price") or 0
            amount = quantity * unit_price
            InvoiceLine.objects.create(
                invoice=invoice,
                description=line.get("description", ""),
                quantity=quantity,
                unit_price=unit_price,
                amount=amount,
            )
