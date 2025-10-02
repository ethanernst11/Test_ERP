from __future__ import annotations

from django.contrib.auth import authenticate, get_user_model, login as django_login, logout as django_logout
from django.db.models import Prefetch
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .filters import UserFilterSet
from .models import Role, user_has_role
from .permissions import IsAdminOrReadOnly
from .serializers import RoleSerializer, UserSerializer, UserUpdateSerializer

User = get_user_model()


class RoleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]


class UserViewSet(viewsets.ModelViewSet):
    queryset = (
        User.objects.all()
        .prefetch_related(Prefetch("erp_roles", queryset=Role.objects.all()))
        .order_by("username")
    )
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filterset_class = UserFilterSet
    search_fields = ["username", "email", "first_name", "last_name"]
    ordering_fields = ["username", "email", "is_active"]

    def get_serializer_class(self):
        if self.request.method in ("POST", "PUT", "PATCH"):
            return UserUpdateSerializer
        return UserSerializer


class AuthViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def create_token_response(self, user: User) -> Response:
        token, _ = Token.objects.get_or_create(user=user)
        serializer = UserSerializer(user, context={"request": self.request})
        return Response({"token": token.key, "user": serializer.data})

    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def login(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        if not username or not password:
            return Response({"detail": "Username and password required."}, status=status.HTTP_400_BAD_REQUEST)
        user = authenticate(request, username=username, password=password)
        if not user:
            return Response({"detail": "Invalid credentials."}, status=status.HTTP_400_BAD_REQUEST)
        if not user.is_active:
            return Response({"detail": "Account is inactive."}, status=status.HTTP_403_FORBIDDEN)
        response = self.create_token_response(user)
        django_login(request, user)
        return response

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def logout(self, request):
        Token.objects.filter(user=request.user).delete()
        django_logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def current_user(self, request):
        serializer = UserSerializer(request.user, context={"request": request})
        role_codes = list(request.user.erp_roles.values_list("code", flat=True))
        return Response({"user": serializer.data, "roles": role_codes, "timestamp": timezone.now()})
