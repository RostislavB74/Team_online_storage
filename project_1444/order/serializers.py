# from rest_framework import serializers
# from .models import Order, OrderItem
# from product.models import Product
from rest_framework import serializers
from .models import Order, OrderItem
from cart.models import Cart, CartItem
class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source="product.name")

    class Meta:
        model = OrderItem
        fields = ["id", "product", "product_name", "quantity", "price"]
class OrderSerializer(serializers.ModelSerializer):
    order_items = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ["id", "user", "order_items", "status", "total_price", "created_at", "updated_at"]

    def get_order_items(self, obj):
        return OrderItemSerializer(obj.order_items.all(), many=True).data

    def create(self, validated_data):
        user = self.context["request"].user
        cart = Cart.objects.get(user=user)  # Отримуємо корзину юзера
        order = Order.objects.create(user=user, total_price=cart.total_price)  # Створюємо замовлення

        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product_price  # Важливо! Використовуємо зафіксовану ціну
            )

        cart.clear()  # Очищуємо корзину після оформлення замовлення
        return order

# from rest_framework import serializers
# from .models import Order, OrderItem
# from cart.models import CartItem  # Імпортуємо CartItem

# class OrderItemSerializer(serializers.ModelSerializer):
#     product_name = serializers.ReadOnlyField(source="product.name")

#     class Meta:
#         model = OrderItem
#         fields = ["id", "product", "product_name", "quantity", "price"]

# class OrderSerializer(serializers.ModelSerializer):
#     order_items = OrderItemSerializer(many=True, read_only=True)

#     class Meta:
#         model = Order
#         fields = ["id", "user", "order_items", "status", "total_price", "created_at", "updated_at"]

#     def create(self, validated_data):
#         user = self.context["request"].user
#         cart_items = CartItem.objects.filter(cart__user=user)

#         if not cart_items.exists():
#             raise serializers.ValidationError("Корзина порожня!")

#         order = Order.objects.create(user=user, **validated_data)

#         # Копіюємо товари з корзини в замовлення
#         for cart_item in cart_items:
#             OrderItem.objects.create(
#                 order=order,
#                 product=cart_item.product,
#                 quantity=cart_item.quantity,
#                 price=cart_item.product_price  # Беремо зафіксовану ціну
#             )

#         # Очищаємо корзину
#         cart_items.first().cart.clear()

#         order.calculate_total_price()
#         return order

# class OrderItemSerializer(serializers.ModelSerializer):
#     product_name = serializers.ReadOnlyField(source="product.name")

#     class Meta:
#         model = OrderItem
#         fields = ["id", "product", "product_name", "quantity", "price"]
# class OrderSerializer(serializers.ModelSerializer):
#     order_items = OrderItemSerializer(many=True, read_only=True)

#     class Meta:
#         model = Order
#         fields = ["id", "user", "order_items", "status", "total_price", "created_at", "updated_at"]

#     def create(self, validated_data):
#         user = self.context["request"].user

#         # Отримуємо всі CartItem для поточного користувача
#         cart_items = CartItem.objects.filter(user=user)

#         if not cart_items.exists():
#             raise serializers.ValidationError("Корзина порожня!")

#         # Створюємо замовлення
#         order = Order.objects.create(user=user, **validated_data)

#         # Копіюємо дані з CartItem в OrderItem
#         for cart_item in cart_items:
#             OrderItem.objects.create(
#                 order=order,
#                 product=cart_item.product,
#                 quantity=cart_item.quantity,
#                 price=cart_item.price  # Використовуємо зафіксовану ціну з CartItem
#             )

#         # Очищаємо корзину після створення замовлення
#         cart_items.delete()

#         order.calculate_total_price()  # Оновлюємо загальну суму
#         return order
# class OrderSerializer(serializers.ModelSerializer):
#     order_items = OrderItemSerializer(many=True)

#     class Meta:
#         model = Order
#         fields = ["id", "user", "order_items", "status", "total_price", "created_at", "updated_at"]
#     def create(self, validated_data):
#         order_items_data = validated_data.pop("order_items")
#         order = Order.objects.create(**validated_data)

#         for item_data in order_items_data:
#             product_id = item_data.pop("product")  # Отримуємо ID
#             product = Product.objects.get(id=product_id)  # Завантажуємо об'єкт продукту
#             price = product.price  # Беремо ціну з продукту
#             OrderItem.objects.create(order=order, product=product, price=price, **item_data)

#         order.calculate_total_price()  # Оновлюємо загальну суму
#         return order
    