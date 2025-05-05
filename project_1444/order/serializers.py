# order/serializers.py
from rest_framework import serializers
from decimal import Decimal
from django.utils.translation import gettext_lazy as _
from .models import Order, OrderItem
from discounts.models import Coupon
from product.models import SubProducts
from drf_spectacular.utils import extend_schema_field
from product.utils import get_discounted_price

class OrderItemCreateSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
    product_price = serializers.DecimalField(max_digits=12, decimal_places=2)

    def validate_product_id(self, value):
        try:
            SubProducts.objects.get(id=value)
        except SubProducts.DoesNotExist:
            raise serializers.ValidationError(_("Продукт з таким ID не існує"))
        return value

class OrderCreateSerializer(serializers.Serializer):
    payment_method = serializers.ChoiceField(
        choices=[('cash', 'cash'), ('liqpay', 'liqpay'), ('googlepay', 'googlepay')],
        default='cash'
    )
    delivery_method = serializers.ChoiceField(
        choices=[('pickup', 'pickup'), ('delivery', 'delivery')],
        default='pickup'
    )
    recipient_name = serializers.CharField(max_length=100, required=False, allow_null=True)
    recipient_phone = serializers.CharField(max_length=20, required=False, allow_null=True)
    address = serializers.CharField(required=False, allow_null=True)
    coupon = serializers.PrimaryKeyRelatedField(
        queryset=Coupon.objects.all(), required=False, allow_null=True
    )
    call_me = serializers.BooleanField(default=False)
    discount = serializers.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'), required=False)
    items = OrderItemCreateSerializer(many=True)

    def validate(self, data):
        """Додаткова валідація"""
        delivery_method = data.get('delivery_method')
        recipient_name = data.get('recipient_name')
        recipient_phone = data.get('recipient_phone')
        address = data.get('address')

        if delivery_method == 'delivery':
            if not recipient_name or not recipient_phone or not address:
                raise serializers.ValidationError(
                    _("Ім’я, телефон і адреса отримувача обов’язкові для доставки")
                )
        elif delivery_method == 'pickup':
            if not recipient_name or not recipient_phone:
                raise serializers.ValidationError(
                    _("Ім’я і телефон отримувача обов’язкові для самовивозу")
                )
            data['address'] = None  # Очищаємо адресу для самовивозу

        items = data.get('items')
        if not items:
            raise serializers.ValidationError(_("Замовлення повинно містити хоча б один товар"))

        return data

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        user = self.context['request'].user if self.context['request'].user.is_authenticated else None
        
        # Створюємо Order
        order = Order.objects.create(
            user=user,
            payment_method=validated_data['payment_method'],
            delivery_method=validated_data['delivery_method'],
            recipient_name=validated_data['recipient_name'],
            recipient_phone=validated_data['recipient_phone'],
            address=validated_data.get('address'),
            coupon=validated_data.get('coupon'),
            call_me=validated_data['call_me'],
            discount=validated_data['discount'],
        )

        # Створюємо OrderItem
        manual_items = []
        for item_data in items_data:
            product = SubProducts.objects.get(id=item_data['product_id'])
            manual_items.append(OrderItem(
                order=order,
                product=product,
                quantity=item_data['quantity'],
                product_price=item_data['product_price'],
            ))
        OrderItem.objects.bulk_create(manual_items)

        # Обчислюємо загальну ціну
        order.calculate_total()
        return order
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
    payment_method = serializers.ChoiceField(
        choices=[('cash', _('Cash')), ('liqpay', 'LiqPay'), ('googlepay', 'GooglePay')],
        default='cash'
    )
    delivery_method = serializers.ChoiceField(
        choices=[('pickup', _('Pickup')), ('delivery', _('Delivery'))],
        default='pickup'
    )
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)
    items = OrderItemSerializer(many=True, read_only=True)
    stocks = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'payment_method', 'delivery_method', 'recipient_name',
            'recipient_phone', 'address', 'coupon', 'call_me', 'total_price',
            'discount', 'final_price', 'status', 'status_pay', 'tracking_number',
            'created_at', 'updated_at', 'items', 'stocks'
        ]

    def get_fields(self):
        fields = super().get_fields()
        fields['items'].context.update(self.context)
        return fields

    def get_stocks(self, obj):
        return [
            {
                'warehouse': stock.warehouse_stock.warehouse.name if stock.warehouse_stock else None,
                'quantity': stock.quantity,
                'in_transit': stock.in_transit
            }
            for stock in obj.stocks.all()
        ]

# from rest_framework import serializers
# from order.models import Order, OrderItem
# from product.models import SubProducts
# from product.utils import get_discounted_price
# from typing import List  # Для типу List[str]
# from drf_spectacular.utils import extend_schema_field
# from decimal import Decimal


# class OrderCreateSerializer(serializers.Serializer):
#     payment_method = serializers.ChoiceField(
#         choices=[('cash', 'Cash'), ('liqpay', 'LiqPay'), ('googlepay', 'GooglePay')],
#         default='cash'
#     )
#     delivery_method = serializers.ChoiceField(
#         choices=[('pickup', 'Pickup'), ('delivery', 'Delivery')],
#         default='pickup'
#     )
#     recipient_name = serializers.CharField(max_length=100, required=True)
#     recipient_phone = serializers.CharField(max_length=20, required=True)
#     address = serializers.CharField(required=True)
#     coupon = serializers.CharField(max_length=50, required=False, allow_null=True)
#     call_me = serializers.BooleanField(default=False)
#     discount = serializers.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'), required=False)

#     def validate(self, data):
#         """Додаткова валідація"""
#         if not data.get('recipient_name') or not data.get('recipient_phone') or not data.get('address'):
#             raise serializers.ValidationError("Ім’я, телефон і адреса отримувача обов’язкові")
#         return data


# class OrderSerializer(serializers.ModelSerializer):
#     items = OrderItemSerializer(many=True, read_only=True)

#     class Meta:
#         model = Order
#         fields = [
#             'id', 'user', 'payment_method', 'delivery_method', 'recipient_name',
#             'recipient_phone', 'address', 'coupon', 'call_me', 'total_price',
#             'discount', 'final_price', 'status', 'created_at', 'updated_at', 'items'
#         ]

#     def get_fields(self):
#         fields = super().get_fields()
#         # Передаємо контекст у вкладений OrderItemSerializer
#         fields['items'].context.update(self.context)
#         return fields

#     def create(self, validated_data):
#         manual_items_data = validated_data.pop('manual_items', [])
#         order = Order.objects.create(**validated_data)
#         OrderItem.objects.bulk_create([OrderItem(order=order, **item) for item in manual_items_data])
#         return order


