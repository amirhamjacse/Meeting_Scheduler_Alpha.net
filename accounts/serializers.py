from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for creating a new user account."""

    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
    )
    password2 = serializers.CharField(
        write_only=True,
        label="Confirm password",
    )

    class Meta:
        model = User
        fields = ["id", "email", "username", "password", "password2"]
        read_only_fields = ["id"]

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password": "Passwords do not match."}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    """Read serializer for the current user's profile."""

    class Meta:
        model = User
        fields = [
            "id", "email", "username", "is_active", "date_joined"
        ]
        read_only_fields = ["id", "is_active", "date_joined"]


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating editable profile fields."""

    class Meta:
        model = User
        fields = ["username"]


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for the change-password endpoint."""

    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
    )
    new_password2 = serializers.CharField(
        write_only=True,
        label="Confirm new password",
    )

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password2"]:
            raise serializers.ValidationError(
                {"new_password": "Passwords do not match."}
            )
        return attrs

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                "Old password is incorrect."
            )
        return value


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Extends the default JWT login response to include user data."""

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data
