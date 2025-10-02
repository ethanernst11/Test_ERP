from __future__ import annotations

from rest_framework.permissions import BasePermission, SAFE_METHODS

from .models import Role, user_has_role


class IsAdmin(BasePermission):
    def has_permission(self, request, view) -> bool:
        return user_has_role(request.user, Role.Code.ADMIN)


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view) -> bool:
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        return user_has_role(request.user, Role.Code.ADMIN)


class IsAdminOrAccountant(BasePermission):
    def has_permission(self, request, view) -> bool:
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        return user_has_role(request.user, Role.Code.ADMIN, Role.Code.ACCOUNTANT)


class IsAccountantOrViewerReadOnly(BasePermission):
    def has_permission(self, request, view) -> bool:
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        return user_has_role(request.user, Role.Code.ADMIN, Role.Code.ACCOUNTANT)
