from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email", "phone", "role"]
        read_only_fields = ["id", "username"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        min_length=8, max_length=128, write_only=True, trim_whitespace=False
    )
    password_confirmation = serializers.CharField(
        max_length=128, write_only=True, trim_whitespace=False
    )

    class Meta:
        model = User
        fields = [
            "username", "first_name", "last_name", "email", "phone",
            "password", "password_confirmation",
        ]
        extra_kwargs = {"email": {"required": True}}

    def validate(self, data):
        if data["password"] != data["password_confirmation"]:
            raise serializers.ValidationError(
                {"password_confirmation": ["Паролі не збігаються."]}
            )
        candidate = User(username=data["username"], email=data["email"])
        try:
            validate_password(data["password"], user=candidate)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"password": list(exc.messages)})
        return data

    def create(self, validated_data):
        validated_data.pop("password_confirmation")
        return User.objects.create_user(**validated_data)


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class AdminUserSerializer(serializers.ModelSerializer):
    """Дані користувача для адміністратора: можна змінити роль та активність."""

    role = serializers.ChoiceField(choices=["user", "admin"], required=False)

    class Meta:
        model = User
        fields = [
            "id", "username", "first_name", "last_name", "email", "phone",
            "role", "is_active", "date_joined",
        ]
        read_only_fields = [
            "id", "username", "first_name", "last_name", "email", "phone", "date_joined",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["role"] = instance.role
        return data

    def update(self, instance, validated_data):
        role = validated_data.pop("role", None)
        if role is not None:
            instance.is_staff = role == "admin"
        return super().update(instance, validated_data)
