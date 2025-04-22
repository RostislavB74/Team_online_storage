from rest_framework import serializers
from order.models import Order, OrderItem
from product.models import SubProducts
from product.utils import get_discounted_price
from typing import List  # Для типу List[str]
from drf_spectacular.utils import extend_schema_field
from decimal import Decimal

class OrderCreateSerializer(serializers.Serializer):
    payment_method = serializers.ChoiceField(
        choices=[('cash', 'Cash'), ('liqpay', 'LiqPay'), ('googlepay', 'GooglePay')],
        default='cash'
    )
    delivery_method = serializers.ChoiceField(
        choices=[('pickup', 'Pickup'), ('delivery', 'Delivery')],
        default='pickup'
    )
    recipient_name = serializers.CharField(max_length=100, required=True)
    recipient_phone = serializers.CharField(max_length=20, required=True)
    address = serializers.CharField(required=True)
    coupon = serializers.CharField(max_length=50, required=False, allow_null=True)
    call_me = serializers.BooleanField(default=False)
    discount = serializers.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'), required=False)

    def validate(self, data):
        """Додаткова валідація"""
        if not data.get('recipient_name') or not data.get('recipient_phone') or not data.get('address'):
            raise serializers.ValidationError("Ім’я, телефон і адреса отримувача обов’язкові")
        return data

class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'product_price', 'total_price']
    @extend_schema_field(str)
    def get_product(self, obj):
        # Безпечно отримуємо user із контексту
        request = self.context.get('request')
        user = request.user if request and hasattr(request, 'user') and request.user.is_authenticated else None
        discounted = get_discounted_price(user, obj.product)
        return {
            'id': obj.product.id,
            'position': obj.product.position,
            'ean_13': obj.product.ean_13,
            'sku': obj.product.sku,
            'article': obj.product.article,
            'weight': obj.product.weight,
            'price': str(obj.product.price),
            'discount_percentage': str(obj.product.discount_percentage or discounted['discount_applied']),
            'new_price': float(discounted['new_price']),
            'old_price': float(discounted['old_price']),
            'discount_applied': float(discounted['discount_applied']),
            'size': obj.product.size,
            'length': obj.product.length,
            'max_length': obj.product.max_length,
            'width': obj.product.width
        }

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'payment_method', 'delivery_method', 'recipient_name',
            'recipient_phone', 'address', 'coupon', 'call_me', 'total_price',
            'discount', 'final_price', 'status', 'created_at', 'updated_at', 'items'
        ]

    def get_fields(self):
        fields = super().get_fields()
        # Передаємо контекст у вкладений OrderItemSerializer
        fields['items'].context.update(self.context)
        return fields

    def create(self, validated_data):
        manual_items_data = validated_data.pop('manual_items', [])
        order = Order.objects.create(**validated_data)
        OrderItem.objects.bulk_create([OrderItem(order=order, **item) for item in manual_items_data])
        return order


