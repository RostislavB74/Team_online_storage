from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import UserProfile, OTP, UserNotificationSettings
from order.serializers import OrderSerializer
from rest_framework import serializers
import re
import json
from django.conf import settings
from .models import UserProfile
from order.models import Order, OrderItem  # Імпортуємо із orders
from product.serializers import ProductSerializer
import re


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")
        if username and password:
            user = authenticate(
                request=self.context.get("request"),
                username=username,
                password=password,
            )
            if not user:
                raise serializers.ValidationError("Invalid credentials")
        else:
            raise serializers.ValidationError("Must include username and password")
        data["user"] = user
        return data


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "password_confirm"]

    def validate(self, data):
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError({"password": "Passwords must match"})
        if User.objects.filter(email=data["email"]).exists():
            raise serializers.ValidationError({"email": "Email already exists"})
        return data

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            is_active=False,
        )
        return user


class OTPSerializer(serializers.Serializer):
    otp_code = serializers.CharField(max_length=6, min_length=6)
    otp_user_id = serializers.IntegerField(required=False)


class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.username", read_only=True)
    avatar = serializers.ImageField(allow_null=True, required=False)
    messengers = serializers.JSONField(default=dict, source="get_messengers_for_admin")
    orders = OrderSerializer(many=True, source="user.orders", read_only=True)

    class Meta:
        model = UserProfile
        fields = ["id", "user", "gender", "messengers", "avatar", "orders"]

    def validate_messengers(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Messengers must be a dictionary")

        allowed_messengers = set(settings.ALLOWED_MESSENGERS)
        for key in value:
            if key not in allowed_messengers:
                raise serializers.ValidationError(f"Unsupported messenger: {key}")

            if key in {"viber", "whatsapp"} and value[key]:
                if not re.match(r"^\+?\d{10,15}$", value[key]):
                    raise serializers.ValidationError(
                        f"Invalid {key} format. Must be a phone number (e.g., +380123456789)"
                    )
            if key == "telegram" and value[key]:
                if not value[key].startswith("@"):
                    raise serializers.ValidationError("Telegram ID must start with @")
            if key == "signal" and value[key] == "":
                raise serializers.ValidationError("Signal ID cannot be empty")

        return value

    def validate_user(self, value):
        request = self.context.get("request")
        if request and not request.user.is_staff:
            raise serializers.ValidationError("Ви не можете змінювати це поле.")
        return value

    def validate_avatar(self, value):
        if value and value.size > 2 * 1024 * 1024:
            raise serializers.ValidationError("Image size must be under 2MB.")
        return value


# class UserProfileSerializer(serializers.ModelSerializer):
#     user = serializers.CharField(source='user.username', read_only=True)
#     avatar = serializers.ImageField(allow_null=True, required=False)
#     messengers = serializers.JSONField(default=dict, source='get_messengers_for_admin')
#     orders = OrderSerializer(many=True, source='user.orders', read_only=True)

#     class Meta:
#         model = UserProfile
#         fields = ["id", "user", "gender", "messengers", "avatar"]

#     def validate_messengers(self, value):
#         if not isinstance(value, dict):
#             raise serializers.ValidationError("Messengers must be a dictionary")

#         allowed_messengers = set(settings.ALLOWED_MESSENGERS)
#         for key in value:
#             if key not in allowed_messengers:
#                 raise serializers.ValidationError(f"Unsupported messenger: {key}")

#             # Валідація формату
#             if key in {'viber', 'whatsapp'} and value[key]:
#                 if not re.match(r'^\+?\d{10,15}$', value[key]):
#                     raise serializers.ValidationError(f"Invalid {key} format. Must be a phone number (e.g., +380123456789)")
#             if key == 'telegram' and value[key]:
#                 if not value[key].startswith('@'):
#                     raise serializers.ValidationError("Telegram ID must start with @")
#             if key == 'signal' and value[key] == '':
#                 raise serializers.ValidationError("Signal ID cannot be empty")

#         return value

#     def validate_user(self, value):
#         request = self.context.get("request")
#         if request and not request.user.is_staff:
#             raise serializers.ValidationError("Ви не можете змінювати це поле.")
#         return value

#     def validate_avatar(self, value):
#         if value and value.size > 2 * 1024 * 1024:
#             raise serializers.ValidationError("Image size must be under 2MB.")
#         return value


class UserNotificationSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserNotificationSettings
        fields = ["email_notifications", "sms_notifications", "viber_notifications"]


class TokenSerializer(serializers.Serializer):
    token = serializers.CharField()
    user_id = serializers.IntegerField()
    username = serializers.CharField()


class LogoutSerializer(serializers.Serializer):
    status = serializers.CharField()
    message = serializers.CharField()
