# Generated manually for initial accounts migration
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Role",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(choices=[("admin", "Admin"), ("accountant", "Accountant"), ("viewer", "Viewer")], max_length=32, unique=True)),
                ("name", models.CharField(max_length=64)),
                ("description", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["code"]},
        ),
        migrations.AddField(
            model_name="role",
            name="users",
            field=models.ManyToManyField(blank=True, related_name="erp_roles", to=settings.AUTH_USER_MODEL),
        ),
    ]
