from django.db import transaction
from rest_framework import serializers
from .models import Cart
from order.models import Order, OrderItem
from warehouse.models import WarehouseStock
from django.db.models import Sum
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from product.models import SubProducts
from .models import Cart
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_field
User = get_user_model()
class CartSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.parent_product", read_only=True)
    total_price = serializers.SerializerMethodField()  # Обчислена ціна окремої позиції
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    username = serializers.CharField(source="user.username", read_only=True) 

    def create(self, validated_data):
        with transaction.atomic():
            cart = Cart.objects.create(**validated_data)
            return cart

    class Meta:
        model = Cart
        fields = ["id", "user", "username", "product", "product_name", "quantity", "total_price", "created_timestamp"]

    @extend_schema_field(str)
    def get_total_price(self, obj):
        """Обчислює загальну ціну для одного товару в корзині"""
        return obj.products_price()

    