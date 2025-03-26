from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema
from .models import Order, OrderItem
from rest_framework.views import APIView
from cart.models import Cart
from .serializers import OrderSerializer, OrderItemSerializer

from discounts.models import (
    PromoCode,
    Coupon,
    BirthdayDiscount,
    PersonalDiscount,
    ProductDiscount,
    BonusAccount,
)
from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema
from .models import Order, OrderItem
from cart.models import Cart

from product.models import Product, SubProducts
from .serializers import OrderSerializer, OrderItemSerializer
from discounts.models import (
    PromoCode,
    Coupon,
    BirthdayDiscount,
    PersonalDiscount,
    ProductDiscount,
)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    @extend_schema(
        request=OrderSerializer,
        responses={201: OrderSerializer},
        description="Створити замовлення з корзини користувача з урахуванням знижок",
    )
    @action(detail=False, methods=["post"], url_path="create-from-cart")
    def create_from_cart(self, request):
        user = request.user if request.user.is_authenticated else None
        session_key = request.session.session_key if not user else None

        if user:
            cart_items = Cart.objects.filter(user=user)
        else:
            if not session_key:
                return Response(
                    {"error": "Сесія не знайдена"}, status=status.HTTP_400_BAD_REQUEST
                )
            cart_items = Cart.objects.filter(session_key=session_key)

        if not cart_items.exists():
            return Response(
                {"error": "Корзина порожня"}, status=status.HTTP_400_BAD_REQUEST
            )

        order_data = {
            "user": user,
            "payment_method": request.data.get("payment_method", "cash"),
            "delivery_method": request.data.get("delivery_method", "pickup"),
            "recipient_name": request.data.get("recipient_name"),
            "recipient_phone": request.data.get("recipient_phone"),
            "coupon": request.data.get("coupon"),
            "call_me": request.data.get("call_me", False),
        }

        if not order_data["recipient_name"] or not order_data["recipient_phone"]:
            return Response(
                {"error": "Ім’я та телефон отримувача обов’язкові"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            order = Order.objects.create(**order_data)
            total_discount = 0
            items_data = []

            for cart_item in cart_items:
                product = cart_item.product.parent_product
                item_price = cart_item.product.price
                item_total = cart_item.products_price()

                discount_percentage = self.get_applicable_discount(
                    user, product, order_data["coupon"]
                )
                if discount_percentage > 0:
                    discount_amount = item_total * (discount_percentage / 100)
                    item_total -= discount_amount
                    total_discount += discount_amount

                items_data.append(
                    OrderItem(
                        order=order,
                        product=product,
                        quantity=cart_item.quantity,
                        product_price=cart_item.product.price,
                        total_price=item_total,
                    )
                )

            OrderItem.objects.bulk_create(items_data)
            order.discount = total_discount
            order.calculate_total()
            cart_items.delete()

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        request=OrderSerializer,
        responses={201: OrderSerializer},
        description="Створити замовлення вручну, вказавши товари",
    )
    @action(detail=False, methods=["post"], url_path="create-manual")
    def create_manual(self, request):
        user = request.user if request.user.is_authenticated else None

        # Отримуємо дані з запиту
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order_data = {
            "user": user,
            "payment_method": serializer.validated_data.get("payment_method", "cash"),
            "delivery_method": serializer.validated_data.get(
                "delivery_method", "pickup"
            ),
            "recipient_name": serializer.validated_data.get("recipient_name"),
            "recipient_phone": serializer.validated_data.get("recipient_phone"),
            "coupon": serializer.validated_data.get("coupon"),
            "call_me": serializer.validated_data.get("call_me", False),
        }

        if not order_data["recipient_name"] or not order_data["recipient_phone"]:
            return Response(
                {"error": "Ім’я та телефон отримувача обов’язкові"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        manual_items = serializer.validated_data.get("manual_items", [])
        if not manual_items:
            return Response(
                {"error": "Потрібно вказати товари для замовлення"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            order = Order.objects.create(**order_data)
            total_discount = 0
            items_data = []

            for item in manual_items:
                product_id = item.get("product")
                quantity = item.get("quantity", 1)
                try:
                    product = Product.objects.get(id=product_id)
                except Product.DoesNotExist:
                    return Response(
                        {"error": f"Товар з ID {product_id} не знайдено"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                item_price = product.price  # Припускаємо, що у Product є поле price
                item_total = item_price * quantity

                discount_percentage = self.get_applicable_discount(
                    user, product, order_data["coupon"]
                )
                if discount_percentage > 0:
                    discount_amount = item_total * (discount_percentage / 100)
                    item_total -= discount_amount
                    total_discount += discount_amount

                items_data.append(
                    OrderItem(
                        order=order,
                        product=product,
                        quantity=quantity,
                        product_price=item_price,
                        total_price=item_total,
                    )
                )

            OrderItem.objects.bulk_create(items_data)
            order.discount = total_discount
            order.calculate_total()

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_applicable_discount(self, user, product, coupon_code):
        max_discount = 0

        if coupon_code:
            promo = PromoCode.objects.filter(code=coupon_code).first()
            if promo and promo.is_valid():
                if (
                    (
                        not promo.applicable_products.exists()
                        and not promo.applicable_categories.exists()
                    )
                    or (product in promo.applicable_products.all())
                    or (product.category in promo.applicable_categories.all())
                ):
                    max_discount = max(max_discount, promo.discount_percentage)
                    promo.use()

        if user:
            coupon = Coupon.objects.filter(user=user, is_active=True).first()
            if coupon and coupon.is_valid():
                max_discount = max(max_discount, coupon.discount_percentage)

            birthday_discount = BirthdayDiscount.objects.filter(user=user).first()
            if birthday_discount and birthday_discount.is_valid():
                max_discount = max(max_discount, birthday_discount.discount_percentage)

            personal = PersonalDiscount.objects.filter(
                user=user, is_active=True
            ).first()
            if personal and personal.is_valid():
                if (
                    (
                        not personal.applicable_products.exists()
                        and not personal.applicable_categories.exists()
                    )
                    or (product in personal.applicable_products.all())
                    or (product.category in personal.applicable_categories.all())
                ):
                    max_discount = max(max_discount, personal.discount_percentage)

        product_discount = ProductDiscount.objects.filter(
            product=product, is_active=True
        ).first()
        if product_discount and product_discount.is_valid():
            max_discount = max(max_discount, product_discount.discount_percentage)

        return max_discount


# class OrderViewSet(viewsets.ModelViewSet):
#     queryset = Order.objects.all()
#     serializer_class = OrderSerializer

#     @extend_schema(
#         request=OrderSerializer,
#         responses={201: OrderSerializer},
#         description="Створити замовлення з корзини користувача з урахуванням знижок"
#     )
#     @action(detail=False, methods=['post'], url_path='create-from-cart')
#     def create_from_cart(self, request):
#         user = request.user if request.user.is_authenticated else None
#         session_key = request.session.session_key if not user else None

#         # Отримуємо корзину
#         if user:
#             cart_items = Cart.objects.filter(user=user)
#         else:
#             if not session_key:
#                 return Response({"error": "Сесія не знайдена"}, status=status.HTTP_400_BAD_REQUEST)
#             cart_items = Cart.objects.filter(session_key=session_key)

#         if not cart_items.exists():
#             return Response({"error": "Корзина порожня"}, status=status.HTTP_400_BAD_REQUEST)

#         # Дані для замовлення
#         order_data = {
#             "user": user,
#             "payment_method": request.data.get("payment_method", "cash"),
#             "delivery_method": request.data.get("delivery_method", "pickup"),
#             "recipient_name": request.data.get("recipient_name"),
#             "recipient_phone": request.data.get("recipient_phone"),
#             "coupon": request.data.get("coupon"),  # Залишаємо поле для промокоду/купона
#             "call_me": request.data.get("call_me", False),
#         }

#         # Перевірка обов’язкових полів
#         if not order_data["recipient_name"] or not order_data["recipient_phone"]:
#             return Response({"error": "Ім’я та телефон отримувача обов’язкові"}, status=status.HTTP_400_BAD_REQUEST)

#         # Створюємо замовлення в транзакції
#         with transaction.atomic():
#             order = Order.objects.create(**order_data)
#             total_discount = 0
#             items_data = []

#             # Обробляємо товари з корзини
#             for cart_item in cart_items:
#                 product = cart_item.product.parent_product
#                 item_price = cart_item.product.price
#                 item_total = cart_item.products_price()

#                 # Перевіряємо знижки для цього товару
#                 discount_percentage = self.get_applicable_discount(user, product, order_data["coupon"])
#                 if discount_percentage > 0:
#                     discount_amount = item_total * (discount_percentage / 100)
#                     item_total -= discount_amount
#                     total_discount += discount_amount

#                 # Додаємо OrderItem
#                 order_item = OrderItem(
#                     order=order,
#                     product=product,
#                     quantity=cart_item.quantity,
#                     product_price=cart_item.product.price,
#                     total_price=item_total
#                 )
#                 items_data.append(order_item)

#             # Зберігаємо всі OrderItem
#             OrderItem.objects.bulk_create(items_data)

#             # Оновлюємо total_price і discount
#             order.discount = total_discount
#             order.calculate_total()

#             # Очищаємо корзину
#             cart_items.delete()

#         serializer = OrderSerializer(order)
#         return Response(serializer.data, status=status.HTTP_201_CREATED)

#     def get_applicable_discount(self, user, product, coupon_code):
#         """Отримує максимальну застосовну знижку для продукту"""
#         max_discount = 0

#         # 1. Перевіряємо PromoCode
#         if coupon_code:
#             promo = PromoCode.objects.filter(code=coupon_code).first()
#             if promo and promo.is_valid():
#                 if (not promo.applicable_products.exists() and not promo.applicable_categories.exists()) or \
#                    (product in promo.applicable_products.all()) or \
#                    (product.category in promo.applicable_categories.all()):
#                     max_discount = max(max_discount, promo.discount_percentage)
#                     promo.use()  # Збільшуємо лічильник використання

#         # 2. Перевіряємо Coupon
#         if user:
#             coupon = Coupon.objects.filter(user=user, is_active=True).first()
#             if coupon and coupon.is_valid():
#                 max_discount = max(max_discount, coupon.discount_percentage)

#             # 3. Перевіряємо BirthdayDiscount
#             birthday_discount = BirthdayDiscount.objects.filter(user=user).first()
#             if birthday_discount and birthday_discount.is_valid():
#                 max_discount = max(max_discount, birthday_discount.discount_percentage)

#             # 4. Перевіряємо PersonalDiscount
#             personal = PersonalDiscount.objects.filter(user=user, is_active=True).first()
#             if personal and personal.is_valid():
#                 if (not personal.applicable_products.exists() and not personal.applicable_categories.exists()) or \
#                    (product in personal.applicable_products.all()) or \
#                    (product.category in personal.applicable_categories.all()):
#                     max_discount = max(max_discount, personal.discount_percentage)

#         # 5. Перевіряємо ProductDiscount
#         product_discount = ProductDiscount.objects.filter(product=product, is_active=True).first()
#         if product_discount and product_discount.is_valid():
#             max_discount = max(max_discount, product_discount.discount_percentage)

#         return max_discount
# from django.conf import settings
# from drf_spectacular.utils import extend_schema
# from rest_framework import viewsets, status
# from rest_framework.response import Response

# from rest_framework.decorators import action
# from django.db import transaction
# from .models import Order, OrderItem
# from cart.models import Cart

# @extend_schema(tags=["Order API"])
# class OrderViewSet(viewsets.ModelViewSet):
#     queryset = Order.objects.all()
#     serializer_class = OrderSerializer

#     @extend_schema(
#         request=OrderSerializer,
#         responses={201: OrderSerializer},
#         description="Створити замовлення з корзини користувача"
#     )
#     @action(detail=False, methods=['post'], url_path='create-from-cart')
#     def create_from_cart(self, request):
#         user = request.user if request.user.is_authenticated else None
#         session_key = request.session.session_key if not user else None

#         # Отримуємо корзину
#         if user:
#             cart_items = Cart.objects.filter(user=user)
#         else:
#             if not session_key:
#                 return Response({"error": "Сесія не знайдена"}, status=status.HTTP_400_BAD_REQUEST)
#             cart_items = Cart.objects.filter(session_key=session_key)

#         if not cart_items.exists():
#             return Response({"error": "Корзина порожня"}, status=status.HTTP_400_BAD_REQUEST)

#         # Дані для замовлення
#         order_data = {
#             "user": user,
#             "payment_method": request.data.get("payment_method", "cash"),
#             "delivery_method": request.data.get("delivery_method", "pickup"),
#             "recipient_name": request.data.get("recipient_name"),
#             "recipient_phone": request.data.get("recipient_phone"),
#             "coupon": request.data.get("coupon"),
#             "call_me": request.data.get("call_me", False),
#         }

#         # Створюємо замовлення в транзакції
#         with transaction.atomic():
#             order = Order.objects.create(**order_data)
#             for cart_item in cart_items:
#                 product = cart_item.product.parent_product
#                 OrderItem.objects.create(
#                     order=order,
#                     product=product,
#                     quantity=cart_item.quantity,
#                     product_price=cart_item.product.price,
#                     total_price=cart_item.products_price()
#                 )
#             if order_data["coupon"]:
#                 discount = self.apply_coupon(order_data["coupon"], order.total_price)
#                 order.discount = discount
#             order.calculate_total()
#             cart_items.delete()

#         serializer = OrderSerializer(order)
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#     def apply_coupon(self, coupon_code, total_price):
#         if coupon_code == "DISCOUNT2024":
#             return total_price * 0.1
#         return 0
