from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Customer",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                ("email", models.EmailField(max_length=254)),
                ("billing_address", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="Invoice",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("number", models.CharField(max_length=32, unique=True)),
                ("description", models.CharField(blank=True, max_length=255)),
                ("status", models.CharField(choices=[
                    ("draft", "Draft"),
                    ("sent", "Sent"),
                    ("paid", "Paid"),
                    ("partial", "Partially Paid"),
                    ("void", "Void"),
                ], default="draft", max_length=16)),
                ("currency", models.CharField(default="USD", max_length=3)),
                ("issue_date", models.DateField()),
                ("due_date", models.DateField()),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="invoices_created", to=settings.AUTH_USER_MODEL)),
                ("customer", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="invoices", to="invoicing.customer")),
            ],
            options={"ordering": ["-issue_date", "-id"]},
        ),
        migrations.CreateModel(
            name="InvoiceLine",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("description", models.CharField(max_length=255)),
                ("quantity", models.DecimalField(decimal_places=2, default="1.00", max_digits=10)),
                ("unit_price", models.DecimalField(decimal_places=2, max_digits=12)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("invoice", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="line_items", to="invoicing.invoice")),
            ],
            options={"ordering": ["id"]},
        ),
        migrations.CreateModel(
            name="Payment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date", models.DateField()),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("method", models.CharField(blank=True, max_length=64)),
                ("reference", models.CharField(blank=True, max_length=64)),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("invoice", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="payments", to="invoicing.invoice")),
            ],
            options={"ordering": ["-date", "-id"]},
        ),
    ]
