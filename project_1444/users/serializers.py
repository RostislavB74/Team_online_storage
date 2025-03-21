from rest_framework import serializers

class OTPRequestSerializer(serializers.Serializer):
    contact = serializers.CharField()

class OTPVerifySerializer(serializers.Serializer):
    contact = serializers.CharField()
    code = serializers.CharField(max_length=6)


from django.contrib.auth import get_user_model
from rest_framework import serializers
from cart.models import Cart
from .serializers import CartSerializer

User = get_user_model()

class UserProfileSerializer(serializers.ModelSerializer):
    cart_items = CartSerializer(many=True, source="cart_set", read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "cart_items"]