from rest_framework import serializers
from .models import Order, OrderItem
from product.models import Product
from django.contrib.auth import get_user_model




class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'product_price', 'total_price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    # Додаємо поля для дозаповнення
    user = serializers.PrimaryKeyRelatedField(queryset=get_user_model().objects.all(), required=False)
    recipient_name = serializers.CharField(required=False)
    recipient_phone = serializers.CharField(required=False)
    # ...інші поля

    class Meta:
        model = Order
        fields = ['id', 'user', 'items', 'payment_method', 'delivery_method',
                  'recipient_name', 'recipient_phone', 'coupon', 'discount', 'status', 'call_me']

    def create(self, validated_data):
        items_data = validated_data.pop('items')  # Забираємо items, так як вони не потрібні при створенні Order
        order = Order.objects.create(**validated_data)
        
        # Тут ми вже створили order, тепер додаємо items
        for item in items_data:
            OrderItem.objects.create(order=order, **item)
        
        # Обчислюємо та оновлюємо загальну суму замовлення
        order.calculate_total()
        return order
