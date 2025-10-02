from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Role

User = get_user_model()


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "code", "name", "description"]


class UserSerializer(serializers.ModelSerializer):
    roles = RoleSerializer(source="erp_roles", many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "roles",
        ]
        read_only_fields = ["username", "email"]


class UserUpdateSerializer(serializers.ModelSerializer):
    role_codes = serializers.ListField(
        child=serializers.ChoiceField(choices=Role.Code.choices),
        required=False,
    )

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "is_active",
            "role_codes",
        ]

    def update(self, instance, validated_data):
        role_codes = validated_data.pop("role_codes", None)
        instance = super().update(instance, validated_data)
        if role_codes is not None:
            roles = Role.objects.filter(code__in=role_codes)
            instance.erp_roles.set(roles)
        return instance
