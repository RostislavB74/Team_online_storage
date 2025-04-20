from rest_framework import serializers
from order.models import Order, OrderItem
from product.models import SubProducts
from product.utils import get_discounted_price
from typing import List  # Для типу List[str]
from drf_spectacular.utils import extend_schema_field

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
    discount = serializers.DecimalField(max_digits=5, decimal_places=2, default=0.00, required=False)

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
        # from rest_framework import serializers
# from order.models import Order, OrderItem
# from product.models import SubProducts
# from product.utils import get_discounted_price
# from drf_spectacular.utils import extend_schema_field
# from typing import List

# class OrderItemSerializer(serializers.ModelSerializer):
#     product = serializers.SerializerMethodField()

#     class Meta:
#         model = OrderItem
#         fields = ['product', 'quantity', 'product_price', 'total_price']
#     @extend_schema_field(List[str])
#     def get_product(self, obj):
#         user = self.context['request'].user if self.context['request'].user.is_authenticated else None
#         discounted = get_discounted_price(user, obj.product)
#         return {
#             'id': obj.product.id,
#             'position': obj.product.position,
#             'ean_13': obj.product.ean_13,
#             'sku': obj.product.sku,
#             'article': obj.product.article,
#             'weight': obj.product.weight,
#             'price': str(obj.product.price),
#             'discount_percentage': str(obj.product.discount_percentage or discounted['discount_applied']),  # Використовуємо discount_applied
#             'new_price': float(discounted['new_price']),
#             'old_price': float(discounted['old_price']),
#             'discount_applied': float(discounted['discount_applied']),
#             'size': obj.product.size,
#             'length': obj.product.length,
#             'max_length': obj.product.max_length,
#             'width': obj.product.width
#         }

# class OrderSerializer(serializers.ModelSerializer):
#     items = OrderItemSerializer(many=True, read_only=True)

#     class Meta:
#         model = Order
#         fields = [
#             'id', 'user', 'payment_method', 'delivery_method', 'recipient_name',
#             'recipient_phone', 'address', 'coupon', 'call_me', 'total_price',
#             'discount', 'final_price', 'status', 'created_at', 'updated_at', 'items'
#         ]
# from rest_framework import serializers
# from .models import Order, OrderItem
# from product.models import SubProducts
# from product.serializers import SubProductsSizesSerializer

# class OrderItemSerializer(serializers.ModelSerializer):
#     product = SubProductsSizesSerializer(read_only=True)
#     product_id = serializers.PrimaryKeyRelatedField(
#         queryset=SubProducts.objects.all(), source='product', write_only=True
#     )

#     class Meta:
#         model = OrderItem
#         fields = ['product', 'product_id', 'quantity', 'product_price', 'total_price']

# class OrderSerializer(serializers.ModelSerializer):
#     items = OrderItemSerializer(many=True, read_only=True)
#     manual_items = OrderItemSerializer(many=True, write_only=True, required=False)

#     class Meta:
#         model = Order
#         fields = [
#             'id', 'user', 'payment_method', 'delivery_method', 'recipient_name',
#             'recipient_phone', 'address', 'coupon', 'call_me', 'total_price',
#             'discount', 'final_price', 'status', 'created_at', 'updated_at',
#             'items', 'manual_items'
#         ]
# class OrderItemSerializer(serializers.ModelSerializer):
#     product = SubProductsSizesSerializer(read_only=True)
#     product_id = serializers.PrimaryKeyRelatedField(
#         queryset=SubProducts.objects.all(), source='product', write_only=True
#     )

#     class Meta:
#         model = OrderItem
#         fields = ['product', 'product_id', 'quantity', 'product_price', 'total_price']

# class OrderSerializer(serializers.ModelSerializer):
#     items = OrderItemSerializer(many=True, read_only=True)
#     manual_items = OrderItemSerializer(many=True, write_only=True, required=False)

#     class Meta:
#         model = Order
#         fields = [
#             'id', 'user', 'payment_method', 'delivery_method', 'recipient_name',
#             'recipient_phone', 'address', 'coupon', 'call_me', 'total_price',
#             'discount', 'final_price', 'status', 'created_at', 'updated_at',
#             'items', 'manual_items'
#         ]

    def create(self, validated_data):
        manual_items_data = validated_data.pop('manual_items', [])
        order = Order.objects.create(**validated_data)
        OrderItem.objects.bulk_create([OrderItem(order=order, **item) for item in manual_items_data])
        return order


# from rest_framework import serializers
# from .models import Order, OrderItem
# from product.models import Product
# from django.contrib.auth import get_user_model
# from django.db import transaction
# from drf_spectacular.utils import extend_schema_field
# from discounts.models import Discount

# from rest_framework import serializers
# from order.models import Order, OrderItem
# from product.models import Product
# from discounts.models import PriceHistory


# class OrderItemSerializer(serializers.ModelSerializer):
#     product_name = serializers.CharField(source="product.name", read_only=True)

#     class Meta:
#         model = OrderItem
#         fields = [
#             "id",
#             "product",
#             "product_name",
#             "quantity",
#             "product_price",
#             "total_price",
#         ]


# class OrderSerializer(serializers.ModelSerializer):
#     items = OrderItemSerializer(many=True, read_only=True)
#     total_price = serializers.DecimalField(
#         max_digits=10, decimal_places=2, read_only=True
#     )

#     class Meta:
#         model = Order
#         fields = [
#             "id",
#             "user",
#             "created_at",
#             "updated_at",
#             "total_price",
#             "payment_method",
#             "delivery_method",
#             "recipient_name",
#             "recipient_phone",
#             "coupon",
#             "discount",
#             "status",
#             "call_me",
#             "items",
#         ]

#     def create(self, validated_data):
#         with transaction.atomic():
#             order = Order.objects.create(**validated_data)
#             # Тут потрібно додати логіку для створення OrderItem із Cart
#             return order

# # orders/serializers.py

# class OrderCreateSerializer(serializers.ModelSerializer):
#     selected_discount = serializers.PrimaryKeyRelatedField(queryset=Discount.objects.all(), required=False)

#     class Meta:
#         model = Order
#         fields = ['selected_discount', '...']

#     def validate_selected_discount(self, discount):
#         user = self.context['request'].user
#         if discount and discount.manual_activation and discount.user != user:
#             raise serializers.ValidationError("Ця знижка не для вас або не активна.")
#         return discount

#     def create(self, validated_data):
#         discount = validated_data.pop('selected_discount', None)
#         order = Order.objects.create(**validated_data)
#         if discount:
#             order.selected_discount = discount
#             total=order.total_price
#             order.final_price = total * (1 - discount.discount_percent / 100)
#             order.old_price = total
#         else:
#             order.final_price = total
#             order.old_price = None
        
