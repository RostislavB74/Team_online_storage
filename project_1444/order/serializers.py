from rest_framework import serializers
from .models import Order, OrderItem
from product.models import Product
from django.contrib.auth import get_user_model
from django.db import transaction
from drf_spectacular.utils import extend_schema_field
from discounts.models import Discount

from rest_framework import serializers
from order.models import Order, OrderItem
from product.models import Product
from discounts.models import PriceHistory


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "product_name",
            "quantity",
            "product_price",
            "total_price",
        ]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "created_at",
            "updated_at",
            "total_price",
            "payment_method",
            "delivery_method",
            "recipient_name",
            "recipient_phone",
            "coupon",
            "discount",
            "status",
            "call_me",
            "items",
        ]

    def create(self, validated_data):
        with transaction.atomic():
            order = Order.objects.create(**validated_data)
            # Тут потрібно додати логіку для створення OrderItem із Cart
            return order

# orders/serializers.py

class OrderCreateSerializer(serializers.ModelSerializer):
    selected_discount = serializers.PrimaryKeyRelatedField(queryset=Discount.objects.all(), required=False)

    class Meta:
        model = Order
        fields = ['selected_discount', '...']

    def validate_selected_discount(self, discount):
        user = self.context['request'].user
        if discount and discount.manual_activation and discount.user != user:
            raise serializers.ValidationError("Ця знижка не для вас або не активна.")
        return discount

    def create(self, validated_data):
        discount = validated_data.pop('selected_discount', None)
        order = Order.objects.create(**validated_data)
        if discount:
            order.selected_discount = discount
            total=order.total_price
            order.final_price = total * (1 - discount.discount_percent / 100)
            order.old_price = total
        else:
            order.final_price = total
            order.old_price = None
        
