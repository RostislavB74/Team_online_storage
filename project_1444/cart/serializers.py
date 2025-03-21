from django.db import transaction
from rest_framework import serializers
from .models import Cart
from order.models import Order, OrderItem
from warehouse.models import WarehouseStock
from django.db.models import Sum
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from .models import Cart
from product.models import SubProducts

class CartSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.parent_product.name", read_only=True)
    product_details = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["id", "user", "product", "product_name", "product_details", "quantity", "total_price", "created_timestamp"]

    def get_product_details(self, obj):
        """Об'єднуємо характеристики в один рядок"""
        return f"{obj.product.length or ''} x {obj.product.width or ''} мм, {obj.product.weight} г"

    def get_total_price(self, obj):
        return obj.products_price()

# class CartItemSerializer(serializers.ModelSerializer):
#     # product_title = serializers.CharField(source='product.title', read_only=True)
#     product_name = serializers.ReadOnlyField(source="product.name")
#     product_price = serializers.ReadOnlyField(source="product.price")
#     total_price = serializers.SerializerMethodField()

#     class Meta:
#         model = CartItem
#         fields = ["id", "product", "product_name", "product_price", "quantity", "total_price"]

#     def get_total_price(self, obj):
#         return obj.product.price * obj.quantity

#     def validate(self, data):
#         """Перевіряємо, чи є товар у достатній кількості на складі перед додаванням у корзину"""
#         product = data["product"]
#         quantity = data["quantity"]
#         stock = WarehouseStock.objects.filter(product=product).aggregate(total=Sum("quantity"))
#         if stock["total"] is None or stock["total"] < quantity:
#             raise serializers.ValidationError("Недостатньо товару на складі.")
#         return data

# class CartSerializer(serializers.ModelSerializer):
#     items = CartItemSerializer(many=True, read_only=True)
#     total_price = serializers.SerializerMethodField()

#     class Meta:
#         model = Cart
#         fields = ["id", "user", "items", "total_price"]
#     @extend_schema_field(serializers.DecimalField(max_digits=10, decimal_places=2))
    
#     def get_total_price(self, obj):
#         return sum(item.product.price * item.quantity for item in obj.items.all())

