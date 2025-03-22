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

class CartSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.parent_product", read_only=True)
    total_price = serializers.SerializerMethodField()  # Обчислена ціна окремої позиції

    class Meta:
        model = Cart
        fields = ["id", "user", "product", "product_name", "quantity", "total_price", "created_timestamp"]

    def get_total_price(self, obj):
        """Обчислює загальну ціну для одного товару в корзині"""
        return obj.products_price()

