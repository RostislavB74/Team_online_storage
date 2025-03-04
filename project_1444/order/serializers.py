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
# from rest_framework import serializers
# from django.db import transaction
# from .models import Order, OrderItem
# from product.models import Product
# from cart.models import Cart, CartItem
# from warehouse.models import WarehouseStock  
# from django.db.models import Sum

# class OrderItemSerializer(serializers.ModelSerializer):
#     product_name = serializers.ReadOnlyField(source="product.name")

#     class Meta:
#         model = OrderItem
#         fields = ["id", "product", "product_name", "quantity", "price"]
# class OrderSerializer(serializers.ModelSerializer):
#     """Створення замовлення на основі кошика"""
#     total_price = serializers.DecimalField(
#         max_digits=10, decimal_places=2, read_only=True
#     )

#     class Meta:
#         model = Order
#         fields = [
#             "id", "user", "status", "payment_method", "delivery_method",
#             "recipient_name", "recipient_phone", "total_price"
#         ]

#     def create(self, validated_data):
#         user = validated_data["user"]
#         cart = Cart.objects.get(user=user)
#         items = cart.items.all()

#         if not items.exists():
#             raise serializers.ValidationError("Корзина порожня.")

#         with transaction.atomic():
#             # Створюємо замовлення з обрахованою сумою
#             order = Order.objects.create(
#                 user=user,
#                 total_price=cart.total_price,  # Беремо загальну вартість із кошика
#                 **validated_data
#             )

#             # Копіюємо всі товари з кошика в замовлення
#             order_items = [
#                 OrderItem(
#                     order=order,
#                     product=item.product,
#                     quantity=item.quantity,
#                     price=item.total_price  # Використовуємо ціну з `CartItem`
#                 )
#                 for item in items
#             ]
#             OrderItem.objects.bulk_create(order_items)

#             # Очищаємо кошик
#             cart.items.all().delete()

#         return order


# class OrderSerializer(serializers.ModelSerializer):
#     """Створення передзамовлення на основі корзини"""
#     items = OrderItemSerializer(many=True, read_only=True)
#     total_price = serializers.DecimalField(
#         max_digits=10, decimal_places=2, read_only=True
#     )

#     class Meta:
#         model = Order
#         fields = [
#             "id", "user", "status", "payment_method", "delivery_method",
#             "recipient_name", "recipient_phone", "total_price", "items"
#         ]
#         read_only_fields = ["total_price", "items"]

#     def create(self, validated_data):
#         user = validated_data.get("user")
#         cart = Cart.objects.get(user=user)
#         items = cart.items.all()

#         if not items.exists():
#             raise serializers.ValidationError("Кошик порожній.")

#         total_price = sum(item.product.price * item.quantity for item in items)

#         with transaction.atomic():
#             order = Order.objects.create(user=user, total_price=total_price, **validated_data)

#             order_items = []
#             for item in items:
#                 # Перевіряємо наявність товару на складі (не резервуємо, лише перевіряємо)
#                 stock_quantity = WarehouseStock.objects.filter(product=item.product).aggregate(total=Sum("quantity"))["total"] or 0
#                 if stock_quantity < item.quantity:
#                     raise serializers.ValidationError(f"Недостатньо товару '{item.product.name}' в наявності.")

#                 order_items.append(
#                     OrderItem(order=order, product=item.product, quantity=item.quantity, price=item.product.price)
#                 )

#             OrderItem.objects.bulk_create(order_items)

#         return order

# from rest_framework import serializers
# from .models import Order, OrderItem
# from product.models import Product
# from cart.models import Cart, CartItem
# from django.db import transaction

# class OrderItemSerializer(serializers.ModelSerializer):
#     product_name = serializers.ReadOnlyField(source="product.name")

#     class Meta:
#         model = OrderItem
#         fields = ["id", "product", "product_name", "quantity", "price"]
# class OrderSerializer(serializers.ModelSerializer):
#     """Створення замовлення на основі корзини"""
#     class Meta:
#         model = Order
#         fields = ["id", "user", "status", "payment_method", "delivery_method", "recipient_name","recipient_phone", "total_price"]

#     def create(self, validated_data):
#         user = validated_data.get("user")
#         cart = Cart.objects.get(user=user)
#         items = cart.items.all()

#         if not items.exists():
#             raise serializers.ValidationError("Корзина порожня.")
        
#         with transaction.atomic():
#             order = Order.objects.create(user=user, **validated_data)
#             for item in items:
#                 stock_entries = Stock.objects.filter(product=item.product).order_by("-quantity")
#                 remaining_quantity = item.quantity
#                 for stock in stock_entries:
#                     if stock.quantity >= remaining_quantity:
#                         stock.quantity -= remaining_quantity
#                         stock.save()
#                         break
#                     else:
#                         remaining_quantity -= stock.quantity
#                         stock.quantity = 0
#                         stock.save()
#                 OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)
#             cart.items.all().delete()
#         return order
