# Generated manually for initial budgets migration
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("ledger", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Budget",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("period_start", models.DateField()),
                ("period_end", models.DateField()),
                ("cadence", models.CharField(choices=[("monthly", "Monthly"), ("quarterly", "Quarterly")], max_length=16)),
                ("amount", models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                ("description", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("account", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="budgets", to="ledger.account")),
                ("created_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="budgets_created", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-period_start", "account__code"]},
        ),
        migrations.AlterUniqueTogether(
            name="budget",
            unique_together={("account", "period_start", "period_end", "cadence")},
        ),
    ]
