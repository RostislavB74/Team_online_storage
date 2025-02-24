from rest_framework import serializers
from .models import Order, OrderItem
from product.models import Product
from rest_framework import serializers
from .models import Order, OrderItem
from cart.models import Cart, CartItem

class OrderItemSerializer(serializers.ModelSerializer):
#     product_name = serializers.ReadOnlyField(source="product.name")

#     class Meta:
#         model = OrderItem
#         fields = ["id", "product", "product_name", "quantity", "price"]

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
 
# class OrderItemSerializer(serializers.ModelSerializer):
#     product_name = serializers.ReadOnlyField(source="product.name")

#     class Meta:
#         model = OrderItem
#         fields = ["id", "product", "product_name", "quantity", "price"]
# class OrderSerializer(serializers.ModelSerializer):
#     order_items = serializers.SerializerMethodField()

#     class Meta:
#         model = Order
#         fields = ["id", "user", "order_items", "status", "total_price", "created_at", "updated_at"]

#     def get_order_items(self, obj):
#         return OrderItemSerializer(obj.order_items.all(), many=True).data

#     def create(self, validated_data):
#         user = self.context["request"].user
#         cart = Cart.objects.get(user=user) 
#         print(cart) # Отримуємо корзину юзера
#         order = Order.objects.create(user=user, total_price=cart.total_price)  # Створюємо замовлення

#         for cart_item in cart.items.all():
#             OrderItem.objects.create(
#                 order=order,
#                 product=cart_item.product,
#                 quantity=cart_item.quantity,
#                 price=cart_item.product_price  # Важливо! Використовуємо зафіксовану ціну
#             )

#         cart.clear()  # Очищуємо корзину після оформлення замовлення
#         return order

from rest_framework import serializers
from .models import Order, OrderItem
from cart.models import CartItem, Cart  # Імпортуємо CartItem

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source="product.name")

    class Meta:
        model = OrderItem
        fields = ["id", "product", "product_name", "quantity", "price"]

class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "user", "order_items", "status", "total_price", "created_at", "updated_at"]

    def create(self, validated_data):
        user = self.context["request"].user
        cart_items = CartItem.objects.filter(cart__user=user)

        if not cart_items.exists():
            raise serializers.ValidationError("Корзина порожня!")

        order = Order.objects.create(user=user, **validated_data)

        # Копіюємо товари з корзини в замовлення
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product_price  # Беремо зафіксовану ціну
            )

        # Очищаємо корзину
        cart_items.first().cart.clear()

        order.calculate_total_price()
        return order

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source="product.name")

    class Meta:
        model = OrderItem
        fields = ["id", "product", "product_name", "quantity", "price"]
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
class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ["id", "user", "order_items", "status", "total_price", "created_at", "updated_at"]
    def create(self, validated_data):
        order_items_data = validated_data.pop("order_items")
        order = Order.objects.create(**validated_data)

        for item_data in order_items_data:
            product_id = item_data.pop("product")  # Отримуємо ID
            product = Product.objects.get(id=product_id)  # Завантажуємо об'єкт продукту
            price = product.price  # Беремо ціну з продукту
            OrderItem.objects.create(order=order, product=product, price=price, **item_data)

        order.calculate_total_price()  # Оновлюємо загальну суму
        return order
    
# def create(self, validated_data):
    #     order_items_data = validated_data.pop("order_items")
    #     order = Order.objects.create(**validated_data)

    #     for item_data in order_items_data:
    #         product_id = item_data["product"]  # Отримуємо ID продукту
    #         product = Product.objects.get(id=product_id)  # Завантажуємо продукт
    #         item_data["product"] = product  # Замінюємо ID на об'єкт
    #         item_data["price"] = product.price  # Додаємо ціну
    #         OrderItem.objects.create(order=order, **item_data)

    #     order.calculate_total_price()  # Оновлюємо загальну суму
    #     return order

# class OrderSerializer(serializers.ModelSerializer):
#     order_items = OrderItemSerializer(many=True, write_only=True)
#     items_detail = OrderItemSerializer(source="order_items", many=True, read_only=True)
#     user = serializers.ReadOnlyField(source="user.username")

#     class Meta:
#         model = Order
#         fields = ["id", "user", "order_items", "items_detail", "status", "total_price", "created_at", "updated_at"]

#     def create(self, validated_data):
#         order_items_data = validated_data.pop("order_items")
#         order = Order.objects.create(**validated_data)
#         for item_data in order_items_data:
#             OrderItem.objects.create(order=order, **item_data)
#         order.calculate_total_price()
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
#             product = item_data["product"]  # Отримуємо продукт
#             price = product.price  # Беремо ціну товару
#             OrderItem.objects.create(order=order, price=price, **item_data)

#         order.calculate_total_price()  # Оновлюємо загальну ціну замовлення
#         return order


# class OrderSerializer(serializers.ModelSerializer):
#     order_items = OrderItemSerializer(many=True)  
#     user = serializers.ReadOnlyField(source="user.username")

#     class Meta:
#         model = Order
#         fields = ["id", "user", "order_items", "status", "total_price", "created_at", "updated_at"]

#     def create(self, validated_data):
#         order_items_data = validated_data.pop("order_items")
#         order = Order.objects.create(**validated_data)
#         for item_data in order_items_data:
#             OrderItem.objects.create(order=order, **item_data)
#         order.calculate_total_price()
#         return order

# class OrderSerializer(serializers.ModelSerializer):
#     order_items = OrderItemSerializer(many=True)  # Видалив read_only=True
#     user = serializers.ReadOnlyField(source="user.username")

#     class Meta:
#         model = Order
#         fields = ["id", "user", "order_items", "status", "total_price", "created_at", "updated_at"]

#     def create(self, validated_data):
#         order_items_data = validated_data.pop("order_items")
#         order = Order.objects.create(**validated_data)
#         for item_data in order_items_data:
#             OrderItem.objects.create(order=order, **item_data)
#         order.calculate_total_price()
#         return order

# class OrderSerializer(serializers.ModelSerializer):
#     order_items = OrderItemSerializer(many=True)  # Видалив read_only=True
#     user = serializers.ReadOnlyField(source="user.username")

#     class Meta:
#         model = Order
#         fields = ["id", "user", "order_items", "status", "total_price", "created_at", "updated_at"]

#     def create(self, validated_data):
#         order_items_data = validated_data.pop("order_items")
#         order = Order.objects.create(**validated_data)
#         for item_data in order_items_data:
#             OrderItem.objects.create(order=order, **item_data)
#         order.calculate_total_price()
#         return order
# class OrderSerializer(serializers.ModelSerializer):
#     order_items = OrderItemSerializer(many=True, read_only=True)  
#     payment_method = serializers.CharField(write_only=True)  # Метод оплати
#     delivery_method = serializers.CharField(write_only=True)  # Метод доставки
#     coupon_code = serializers.CharField(required=False, allow_blank=True, write_only=True)  # Промокод
#     apply_discount = serializers.BooleanField(default=False, write_only=True)  # Чи застосовувати персональну знижку
#     call_me = serializers.BooleanField(default=False, write_only=True)  # Чи треба передзвонити

#     class Meta:
#         model = Order
#         fields = [
#             "id", "user", "order_items", "status", "total_price", "created_at", "updated_at",
#             "payment_method", "delivery_method", "coupon_code", "apply_discount", "call_me"
#         ]
#     def create(self, validated_data):
#         user = validated_data["user"]
#         print(f"Створення замовлення для {user}")  # Додаємо лог

#     def create(self, validated_data):
#         """Створення замовлення на основі корзини"""
#         user = validated_data["user"]
#         payment_method = validated_data.pop("payment_method")
#         delivery_method = validated_data.pop("delivery_method")
#         coupon_code = validated_data.pop("coupon_code", None)
#         apply_discount = validated_data.pop("apply_discount", False)
#         call_me = validated_data.pop("call_me", False)

#         # Отримуємо корзину користувача
#         cart = Cart.objects.filter(user=user).first()
#         if not cart or not cart.items.exists():
#             raise serializers.ValidationError("Кошик порожній або не існує.")

#         # Створюємо замовлення
#         order = Order.objects.create(
#             user=user,
#             status="pending",
#             total_price=0,  # Будемо рахувати
#             payment_method=payment_method,
#             delivery_method=delivery_method,
#             coupon_code=coupon_code,
#             apply_discount=apply_discount,
#             call_me=call_me
#         )

#         total_price = 0  # Загальна сума замовлення

#         # Переносимо товари з корзини в замовлення
#         for cart_item in cart.items.all():
#             order_item = OrderItem.objects.create(
#                 order=order,
#                 product=cart_item.product,
#                 quantity=cart_item.quantity,
#                 price=cart_item.product.price  # Беремо актуальну ціну
#             )
#             total_price += order_item.price * order_item.quantity  # Оновлюємо загальну суму

#         # Застосовуємо купон, якщо є
#         discount_amount = self.apply_coupon(coupon_code, total_price) if coupon_code else 0
#         total_price -= discount_amount  # Віднімаємо знижку

#         # Оновлюємо загальну суму в замовленні
#         order.total_price = total_price
#         order.save()

#         # Очищаємо корзину
#         cart.items.all().delete()

#         return order

#     def apply_coupon(self, coupon_code, total_price):
#         """Перевіряємо купон і повертаємо розмір знижки"""
#         # Тут можна реалізувати логіку перевірки купона в БД
#         if coupon_code == "DISCOUNT10":
#             return total_price * 0.1  # 10% знижка
#         return 0


# from rest_framework import serializers
# from .models import Order, OrderItem
# from product.models import Product
# from rest_framework import serializers
# from .models import Order, OrderItem
# from cart.models import Cart, CartItem

# class OrderItemSerializer(serializers.ModelSerializer):
#     product_name = serializers.ReadOnlyField(source="product.name")

#     class Meta:
#         model = OrderItem
#         fields = ["id", "product", "product_name", "quantity", "price"]

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
    