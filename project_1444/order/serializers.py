from rest_framework import serializers
from .models import Order, OrderItem
from product.models import Product
from django.contrib.auth import get_user_model




class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'product_price', 'total_price']

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'product_price', 'total_price']
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = serializers.PrimaryKeyRelatedField(queryset=get_user_model().objects.all(), required=False)
    recipient_name = serializers.CharField(required=False)
    recipient_phone = serializers.CharField(required=False)
    discount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)  # ВАЖЛИВО!

    class Meta:
        model = Order
        fields = ['id', 'user', 'items', 'payment_method', 'delivery_method',
                  'recipient_name', 'recipient_phone', 'coupon', 'discount', 'status', 'call_me']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])  # Забираємо items (вони передаються окремо)
        coupon_code = validated_data.pop('coupon', None)  # Отримуємо купон
        order = Order.objects.create(**validated_data)

        # Додаємо товари в замовлення
        total_price = 0
        for item in items_data:
            product = item['product']
            quantity = item['quantity']
            product_price = product.price  # Беремо ціну лише з продукту!
            total_price += product_price * quantity
            OrderItem.objects.create(order=order, product=product, quantity=quantity, product_price=product_price)

        # Розраховуємо знижку
        discount = self.calculate_discount(coupon_code, total_price)
        order.discount = discount
        order.total_price = total_price - discount
        order.save()
        return order

    def calculate_discount(self, coupon_code, total_price):
        """Перевірка купона та розрахунок знижки"""
        if coupon_code == "DISCOUNT2024":  # Тут має бути нормальна перевірка
            return total_price * 0.1  # 10% знижки
        return 0