from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import UserAddress, UserProfile, User
class OTPRequestSerializer(serializers.Serializer):
    contact = serializers.CharField()

class OTPVerifySerializer(serializers.Serializer):
    contact = serializers.CharField()
    code = serializers.CharField(max_length=6)


class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)

    class Meta:
        model = UserProfile
        fields = ["id", "user", "gender", "viber", "telegram"]

    def validate_user(self, value):
        # Якщо юзер не є адміністратором, забороняємо зміну user_id
        request = self.context.get("request")
        if request and not request.user.is_staff:
            raise serializers.ValidationError("Ви не можете змінювати це поле.")
        return value


class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddress
        fields = ["id", "user", "delivery_type", "city", "street", "postal_code", "nova_poshta_branch", "is_default"]

    def validate(self, data):
        """Валідація полів залежно від типу доставки"""
        delivery_type = data.get("delivery_type")

        if delivery_type == "home":
            if not data.get("street") or not data.get("postal_code"):
                raise serializers.ValidationError("Для звичайної адреси необхідно вказати вулицю та поштовий індекс.")
        
        elif delivery_type == "nova_poshta":
            if not data.get("nova_poshta_branch"):
                raise serializers.ValidationError("Для Нової Пошти необхідно вказати номер відділення або поштомату.")
            data["postal_code"] = "1234"  # Автоматично встановлюємо значення для НП

        return data



class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])

class DeleteAccountSerializer(serializers.Serializer):
    password = serializers.CharField(required=True)

    def validate(self, data):
        user = self.context["request"].user
        if not user.check_password(data["password"]):
            raise serializers.ValidationError("Невірний пароль")
        return data
