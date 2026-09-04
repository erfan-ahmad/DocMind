# accounts_app/serializers.py
from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


class UserSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined', 'password2',
                  'password')
        read_only_fields = ('id', 'date_joined', 'is_active')

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value

    def validate_email(self, value):
        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError("Enter a valid email address.")

        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError("Password must contain at least one digit.")
        if not any(char.isupper() for char in value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        return value

    def validate(self, data):
        if data.get("password") != data.get("password2"):
            raise serializers.ValidationError({"password": "Passwords don't match"})
        return data

    def create(self, validated_data):
        validated_data.pop("password2")

        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ''),
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ''),
            last_name=validated_data.get("last_name", '')
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    ✅ استفاده از Serializer به جای ModelSerializer برای لاگین
    """
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        # بررسی وجود username و password
        if not username or not password:
            raise serializers.ValidationError({
                "detail": "Username and password are required"
            })

        # احراز هویت کاربر
        user = authenticate(username=username, password=password)

        if not user:
            raise serializers.ValidationError({
                "detail": "Invalid credentials"
            })

        if not user.is_active:
            raise serializers.ValidationError({
                "detail": "This account has been disabled"
            })

        # ✅ برگرداندن کاربر
        return {'user': user}