import logging

from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from core.permissions import IsAdmin

from .models import User
from .serializers import (
    AdminUserSerializer,
    LogoutSerializer,
    RegisterSerializer,
    UserSerializer,
)

logger = logging.getLogger(__name__)


class RegisterView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        logger.info("Зареєстровано користувача id=%s", user.pk)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class LogoutView(APIView):
    """Додає refresh-токен до чорного списку, після чого його не можна використати."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            RefreshToken(serializer.validated_data["refresh"]).blacklist()
        except TokenError:
            raise ValidationError({"refresh": ["Токен недійсний або вже використаний."]})
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class UserListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        users = User.objects.order_by("id")
        return Response(AdminUserSerializer(users, many=True).data)


class UserDetailView(APIView):
    permission_classes = [IsAdmin]

    def get_user(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            logger.warning("Не знайдено користувача id=%s", pk)
            raise NotFound(f"Користувача з id={pk} не знайдено.")

    def get(self, request, pk):
        return Response(AdminUserSerializer(self.get_user(pk)).data)

    def patch(self, request, pk):
        user = self.get_user(pk)
        if user == request.user and (
            request.data.get("role") == "user" or request.data.get("is_active") is False
        ):
            raise ValidationError(
                {"role": ["Не можна забрати права адміністратора або заблокувати себе."]}
            )
        serializer = AdminUserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        logger.info("Адміністратор id=%s змінив користувача id=%s", request.user.pk, pk)
        return Response(serializer.data)
