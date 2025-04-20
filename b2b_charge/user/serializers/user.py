from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email
from django.db.models import Sum
from rest_framework import serializers

from user.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        read_only_fields = (
            "is_staff",
            "is_superuser",
            "full_name",
            "phone_number",
            "email",
        )
        exclude = (
            "password",
            "user_permissions",
            "is_staff",
            "is_superuser",
            "last_login",
        )


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "phone_number",
            "full_name",
            "first_name",
            "last_name",
            "avatar",
        ]


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    """

    password = serializers.CharField(write_only=True, min_length=8, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "confirm_password",
            "first_name",
            "last_name",
            "phone_number",
        ]

    def validate_email(self, value):
        """
        Validate the email format and uniqueness.
        """
        if value:
            validate_email(value)
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError(
                    "A user with this email already exists."
                )
        return value

    def validate_username(self, value):
        """
        Ensure the username is unique and meets criteria.
        """
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "A user with this username already exists."
            )
        return value

    def validate(self, data):
        """
        Ensure passwords match and meet criteria.
        """
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )

        validate_password(data["password"])

        return data

    def create(self, validated_data):
        """
        Create a new user instance.
        """
        validated_data.pop("confirm_password")
        return User.objects.create(**validated_data)
