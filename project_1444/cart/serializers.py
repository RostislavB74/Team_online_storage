from django.db import transaction
from rest_framework import serializers
from .models import Cart, CartItem
from order.models import Order, OrderItem
from warehouse.models import WarehouseStock
from django.db.models import Sum
class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source="product.name")
    product_price = serializers.ReadOnlyField(source="product.price")
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ["id", "product", "product_name", "product_price", "quantity", "total_price"]

    def get_total_price(self, obj):
        return obj.product.price * obj.quantity

    def validate(self, data):
        """Перевіряємо, чи є товар у достатній кількості на складі перед додаванням у корзину"""
        product = data["product"]
        quantity = data["quantity"]
        stock = WarehouseStock.objects.filter(product=product).aggregate(total=Sum("quantity"))
        if stock["total"] is None or stock["total"] < quantity:
            raise serializers.ValidationError("Недостатньо товару на складі.")
        return data

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["id", "user", "items", "total_price"]

    def get_total_price(self, obj):
        return sum(item.product.price * item.quantity for item in obj.items.all())

# from rest_framework import serializers
# from .models import Cart, CartItem
# from product.models import Product

# class CartItemSerializer(serializers.ModelSerializer):
#     product_name = serializers.ReadOnlyField(source="product.name")
#     product_price = serializers.ReadOnlyField(source="product.price")
#     total_price = serializers.SerializerMethodField()

#     class Meta:
#         model = CartItem
#         fields = ["id", "product", "product_name", "product_price", "quantity", "total_price"]

#     def get_total_price(self, obj):
#         return obj.total_price

# class CartSerializer(serializers.ModelSerializer):
#     items = CartItemSerializer(many=True, read_only=True)
#     total_price = serializers.SerializerMethodField()

#     class Meta:
#         model = Cart
#         fields = ["id", "user", "items", "total_price"]

#     def get_total_price(self, obj):
#         return obj.total_price
