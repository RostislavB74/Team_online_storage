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
            # Обрахунок знижки
            total = ...  # сума з товарів у замовленні
            discounted = total * (1 - discount.discount_percent / 100)
            order.final_price = discounted
        else:
            order.final_price = ...  # звичайна сума

        order.save()
        return order

# class OrderItemSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = OrderItem
#         fields = ['product', 'quantity', 'product_price', 'total_price']

# class OrderSerializer(serializers.ModelSerializer):
#     items = OrderItemSerializer(many=True, read_only=True)
#     user = serializers.PrimaryKeyRelatedField(queryset=get_user_model().objects.all(), required=False)
#     recipient_name = serializers.CharField(required=False)
#     recipient_phone = serializers.CharField(required=False)
#     discount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)  # ВАЖЛИВО!

#     class Meta:
#         model = Order
#         fields = ['id', 'user', 'items', 'payment_method', 'delivery_method',
#                   'recipient_name', 'recipient_phone', 'coupon', 'discount', 'status', 'call_me']

#     def create(self, validated_data):
#         items_data = validated_data.pop('items', [])  # Забираємо items (вони передаються окремо)
#         coupon_code = validated_data.pop('coupon', None)  # Отримуємо купон
#         order = Order.objects.create(**validated_data)

#         # Додаємо товари в замовлення
#         total_price = 0
#         for item in items_data:
#             product = item['product']
#             quantity = item['quantity']
#             product_price = product.price  # Беремо ціну лише з продукту!
#             total_price += product_price * quantity
#             OrderItem.objects.create(order=order, product=product, quantity=quantity, product_price=product_price)

#         # Розраховуємо знижку
#         discount = self.calculate_discount(coupon_code, total_price)
#         order.discount = discount
#         order.total_price = total_price - discount
#         order.save()
#         return order

#     def calculate_discount(self, coupon_code, total_price):
#         """Перевірка купона та розрахунок знижки"""
#         if coupon_code == "DISCOUNT2024":  # Тут має бути нормальна перевірка
#             return total_price * 0.1  # 10% знижки
