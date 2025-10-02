from __future__ import annotations

from django.conf import settings
from django.db import models


class Role(models.Model):
    class Code(models.TextChoices):
        ADMIN = "admin", "Admin"
        ACCOUNTANT = "accountant", "Accountant"
        VIEWER = "viewer", "Viewer"

    code = models.CharField(max_length=32, choices=Code.choices, unique=True)
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True)
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="erp_roles",
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["code"]

    def __str__(self) -> str:
        return self.name

    @staticmethod
    def default_roles() -> list[tuple[str, str]]:
        return [
            (Role.Code.ADMIN, "Admin"),
            (Role.Code.ACCOUNTANT, "Accountant"),
            (Role.Code.VIEWER, "Viewer"),
        ]


def user_has_role(user, *codes: str) -> bool:
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    user_codes = set(user.erp_roles.values_list("code", flat=True))
    return any(code in user_codes for code in codes)
