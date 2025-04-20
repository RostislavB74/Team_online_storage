from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema
from order.tasks import send_order_confirmation_email
from order.models import Order, OrderItem
from cart.models import Cart
from product.models import SubProducts
from order.serializers import OrderSerializer, OrderCreateSerializer
from product.utils import get_discounted_price
from users.models import UserProfile
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user if self.request.user.is_authenticated else None)

    @extend_schema(
        request=OrderCreateSerializer,
        responses={201: OrderSerializer},
        description="Створити замовлення з корзини користувача з урахуванням знижок",
    )
    @action(detail=False, methods=["post"], url_path="create-from-cart")
    def create_from_cart(self, request):
        logger.info(f"Received create-from-cart request: {request.data}")
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order_data = serializer.validated_data
        logger.info(f"Validated order data: {order_data}")

        user = request.user if request.user.is_authenticated else None
        session_key = request.session.session_key if not user else None
        logger.info(f"User: {user}, Session key: {session_key}")

        if user:
            try:
                profile = user.profile
                logger.info(f"User profile: phone={profile.phone}, address={profile.address}")
            except UserProfile.DoesNotExist:
                profile = None
                logger.warning("User profile does not exist")
        else:
            profile = None
            logger.info("No user, using anonymous session")

        if user:
            cart_items = Cart.objects.filter(user=user)
        else:
            if not session_key:
                logger.error("Session key not found")
                return Response(
                    {"error": "Сесія не знайдена"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            cart_items = Cart.objects.filter(session_key=session_key)

        logger.info(f"Cart items count: {cart_items.count()}")
        if not cart_items.exists():
            logger.error("Cart is empty")
            return Response(
                {"error": "Корзина порожня"},
                status=status.HTTP_400_BAD_REQUEST
            )

        order_data_dict = {
            "user": user,
            "payment_method": order_data.get("payment_method", "cash"),
            "delivery_method": order_data.get("delivery_method", "pickup"),
            "recipient_name": order_data.get("recipient_name"),
            "recipient_phone": order_data.get("recipient_phone"),
            "address": order_data.get("address"),
            "coupon": order_data.get("coupon"),
            "call_me": order_data.get("call_me", False),
            "discount": order_data.get("discount", Decimal('0.00'))
        }
        logger.info(f"Order data dict: {order_data_dict}")

        with transaction.atomic():
            order = Order.objects.create(**order_data_dict)
            logger.info(f"Created order ID: {order.id}")
            items_data = []

            for cart_item in cart_items:
                subproduct = cart_item.product
                if not SubProducts.objects.filter(id=subproduct.id).exists():
                    logger.warning(f"Subproduct ID {subproduct.id} does not exist")
                    continue

                discounted = get_discounted_price(user, subproduct)
                item_price = discounted['new_price']
                item_total = item_price * cart_item.quantity
                logger.info(f"Subproduct: {subproduct}, Price: {item_price}, Total: {item_total}")

                items_data.append(
                    OrderItem(
                        order=order,
                        product=subproduct,
                        quantity=cart_item.quantity,
                        product_price=item_price,
                        total_price=item_total,
                    )
                )

            if not items_data:
                order.delete()
                logger.error("No valid items in cart")
                return Response(
                    {"error": "Жоден товар у кошику не доступний"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            OrderItem.objects.bulk_create(items_data)
            logger.info(f"Created {len(items_data)} order items")
            order.calculate_total()  # Обчислюємо total_price і final_price
            logger.info(f"Order total_price: {order.total_price}, final_price: {order.final_price}")
            cart_items.delete()

            # Якщо обрано LiqPay або GooglePay, повертаємо URL для оплати
            if order_data_dict['payment_method'] in ['liqpay', 'googlepay']:
                payment_url = f"/api/payment/pay/{order.id}/"
                logger.info(f"Returning payment URL: {payment_url}")
                return Response(
                    {
                        "payment_url": payment_url,
                        "order": OrderSerializer(order, context={'request': request}).data
                    },
                    status=status.HTTP_201_CREATED
                )

            # Відправка email для інших методів оплати
            if order.user and order.user.email:
                logger.info(f"Sending order confirmation email to {order.user.email}")
                send_order_confirmation_email.delay(order.id, order.user.email)

        serializer = OrderSerializer(order, context={'request': request})
        logger.info("Order created successfully")
        return Response(serializer.data, status=status.HTTP_201_CREATED)
# from django.db import transaction
# from rest_framework import viewsets, status
# from rest_framework.response import Response
# from rest_framework.decorators import action
# from drf_spectacular.utils import extend_schema
# from django.core.mail import send_mail
# from .models import Order, OrderItem
# from cart.models import Cart
# from product.models import SubProducts
# from .serializers import OrderSerializer, OrderItemSerializer
# from discounts.models import PromoCode, Coupon, BirthdayDiscount, PersonalDiscount, ProductDiscount
# from product.utils import get_discounted_price
# from users.models import UserProfile
# from decimal import Decimal
# from django.db import transaction
# from rest_framework import viewsets, status
# from rest_framework.response import Response
# from rest_framework.decorators import action
# from drf_spectacular.utils import extend_schema
# # from order.tasks import send_order_confirmation_email  # Імпорт задачі
# from order.models import Order, OrderItem
# from cart.models import Cart
# from product.models import SubProducts
# from order.serializers import OrderSerializer, OrderItemSerializer
# from discounts.models import PromoCode, Coupon, BirthdayDiscount, PersonalDiscount, ProductDiscount
# from product.utils import get_discounted_price
# from users.models import UserProfile
# from decimal import Decimal

# class OrderViewSet(viewsets.ModelViewSet):
#     queryset = Order.objects.all()
#     serializer_class = OrderSerializer

#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user if self.request.user.is_authenticated else None)

#     @extend_schema(
#         request=OrderSerializer,
#         responses={201: OrderSerializer},
#         description="Створити замовлення з корзини користувача з урахуванням знижок",
#     )
#     @action(detail=False, methods=["post"], url_path="create-from-cart")
#     def create_from_cart(self, request):
#         user = request.user if request.user.is_authenticated else None
#         session_key = request.session.session_key if not user else None

#         if user:
#             try:
#                 profile = user.profile
#                 if not profile.phone or not profile.address:
#                     return Response(
#                         {"error": "Заповніть профіль (телефон і адресу)"},
#                         status=status.HTTP_400_BAD_REQUEST
#                     )
#             except UserProfile.DoesNotExist:
#                 return Response(
#                     {"error": "Профіль не знайдено"},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#         if user:
#             cart_items = Cart.objects.filter(user=user)
#         else:
#             if not session_key:
#                 return Response(
#                     {"error": "Сесія не знайдена"},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
#             cart_items = Cart.objects.filter(session_key=session_key)

#         if not cart_items.exists():
#             return Response(
#                 {"error": "Корзина порожня"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         order_data = {
#             "user": user,
#             "payment_method": request.data.get("payment_method", "cash"),
#             "delivery_method": request.data.get("delivery_method", "pickup"),
#             "recipient_name": request.data.get("recipient_name"),
#             "recipient_phone": request.data.get("recipient_phone"),
#             "address": profile.address if user else request.data.get("address"),
#             "coupon": request.data.get("coupon"),
#             "call_me": request.data.get("call_me", False),
#         }

#         if not order_data["recipient_name"] or not order_data["recipient_phone"] or not order_data["address"]:
#             return Response(
#                 {"error": "Ім’я, телефон і адреса отримувача обов’язкові"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         with transaction.atomic():
#             order = Order.objects.create(**order_data)
#             total_discount = Decimal('0.00')
#             items_data = []

#             for cart_item in cart_items:
#                 subproduct = cart_item.product
#                 if not SubProducts.objects.filter(id=subproduct.id).exists():
#                     continue

#                 item_price = get_discounted_price(user, subproduct)['new_price']
#                 item_total = item_price * cart_item.quantity

#                 items_data.append(
#                     OrderItem(
#                         order=order,
#                         product=subproduct,
#                         quantity=cart_item.quantity,
#                         product_price=item_price,
#                         total_price=item_total,
#                     )
#                 )

#             if not items_data:
#                 order.delete()
#                 return Response(
#                     {"error": "Жоден товар у кошику не доступний"},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#             OrderItem.objects.bulk_create(items_data)
#             order.calculate_total()
#             cart_items.delete()

#             # Виклик задачі Celery для асинхронної відправки email
#             if order.user and order.user.email:
#                 send_order_confirmation_email.delay(order.id, order.user.email)

#         serializer = OrderSerializer(order)
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
# class OrderViewSet(viewsets.ModelViewSet):
#     queryset = Order.objects.all()
#     serializer_class = OrderSerializer

#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user if self.request.user.is_authenticated else None)

#     @extend_schema(
#         request=OrderSerializer,
#         responses={201: OrderSerializer},
#         description="Створити замовлення з корзини користувача з урахуванням знижок",
#     )
#     @action(detail=False, methods=["post"], url_path="create-from-cart")
#     def create_from_cart(self, request):
#         user = request.user if request.user.is_authenticated else None
#         session_key = request.session.session_key if not user else None

#         # Перевірка профілю
#         if user:
#             try:
#                 profile = user.profile
#                 if not profile.phone or not profile.address:
#                     return Response(
#                         {"error": "Заповніть профіль (телефон і адресу)"},
#                         status=status.HTTP_400_BAD_REQUEST
#                     )
#             except UserProfile.DoesNotExist:
#                 return Response(
#                     {"error": "Профіль не знайдено"},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#         # Отримуємо кошик
#         if user:
#             cart_items = Cart.objects.filter(user=user)
#         else:
#             if not session_key:
#                 return Response(
#                     {"error": "Сесія не знайдена"}, 
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
#             cart_items = Cart.objects.filter(session_key=session_key)

#         if not cart_items.exists():
#             return Response(
#                 {"error": "Корзина порожня"}, 
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         # Дані замовлення
#         order_data = {
#             "user": user,
#             "payment_method": request.data.get("payment_method", "cash"),
#             "delivery_method": request.data.get("delivery_method", "pickup"),
#             "recipient_name": request.data.get("recipient_name"),
#             "recipient_phone": request.data.get("recipient_phone"),
#             "address": profile.address if user else request.data.get("address"),
#             "coupon": request.data.get("coupon"),
#             "call_me": request.data.get("call_me", False),
#         }

#         if not order_data["recipient_name"] or not order_data["recipient_phone"] or not order_data["address"]:
#             return Response(
#                 {"error": "Ім’я, телефон і адреса отримувача обов’язкові"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         with transaction.atomic():
#             order = Order.objects.create(**order_data)
#             total_discount = Decimal('0.00')
#             items_data = []

#             for cart_item in cart_items:
#                 subproduct = cart_item.product
#                 if not SubProducts.objects.filter(id=subproduct.id).exists():
#                     continue

#                 item_price = get_discounted_price(user, subproduct)['new_price']
#                 item_total = item_price * cart_item.quantity

#                 items_data.append(
#                     OrderItem(
#                         order=order,
#                         product=subproduct,
#                         quantity=cart_item.quantity,
#                         product_price=item_price,
#                         total_price=item_total,
#                     )
#                 )

#             if not items_data:
#                 order.delete()
#                 return Response(
#                     {"error": "Жоден товар у кошику не доступний"},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#             OrderItem.objects.bulk_create(items_data)
#             order.calculate_total()
#             cart_items.delete()

#             # Відправка email
#             if order.user and order.user.email:
#                 try:
#                     send_mail(
#                         'Замовлення підтверджено',
#                         f'Ваше замовлення #{order.id} оформлено! Сума: {order.final_price} грн',
#                         'from@example.com',
#                         [order.user.email],
#                         fail_silently=True,
#                     )
#                 except Exception as e:
#                     print(f"Помилка відправки email: {e}")

#         serializer = OrderSerializer(order)
#         return Response(serializer.data, status=status.HTTP_201_CREATED)

    # ... (create_manual і get_applicable_discount без змін)
# from django.db import transaction
# from rest_framework import viewsets, status
# from rest_framework.response import Response
# from rest_framework.decorators import action
# from drf_spectacular.utils import extend_schema
# from .models import Order, OrderItem
# from cart.models import Cart
# from product.models import SubProducts
# from .serializers import OrderSerializer, OrderItemSerializer
# from discounts.models import PromoCode, Coupon, BirthdayDiscount, PersonalDiscount, ProductDiscount
# from product.utils import get_discounted_price
# from users.models import UserProfile
# from decimal import Decimal

# class OrderViewSet(viewsets.ModelViewSet):
#     queryset = Order.objects.all()
#     serializer_class = OrderSerializer

#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user if self.request.user.is_authenticated else None)

#     @extend_schema(
#         request=OrderSerializer,
#         responses={201: OrderSerializer},
#         description="Створити замовлення з корзини користувача з урахуванням знижок",
#     )
#     @action(detail=False, methods=["post"], url_path="create-from-cart")
#     def create_from_cart(self, request):
#         user = request.user if request.user.is_authenticated else None
#         session_key = request.session.session_key if not user else None

#         # Перевірка профілю
#         if user:
#             try:
#                 profile = user.profile
#                 if not profile.phone or not profile.address:
#                     return Response(
#                         {"error": "Заповніть профіль (телефон і адресу)"},
#                         status=status.HTTP_400_BAD_REQUEST
#                     )
#             except UserProfile.DoesNotExist:
#                 return Response(
#                     {"error": "Профіль не знайдено"},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#         # Отримуємо кошик
#         if user:
#             cart_items = Cart.objects.filter(user=user)
#         else:
#             if not session_key:
#                 return Response(
#                     {"error": "Сесія не знайдена"}, 
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
#             cart_items = Cart.objects.filter(session_key=session_key)

#         if not cart_items.exists():
#             return Response(
#                 {"error": "Корзина порожня"}, 
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         # Дані замовлення
#         order_data = {
#             "user": user,
#             "payment_method": request.data.get("payment_method", "cash"),
#             "delivery_method": request.data.get("delivery_method", "pickup"),
#             "recipient_name": request.data.get("recipient_name"),
#             "recipient_phone": request.data.get("recipient_phone"),
#             "address": profile.address if user else request.data.get("address"),
#             "coupon": request.data.get("coupon"),
#             "call_me": request.data.get("call_me", False),
#         }

#         if not order_data["recipient_name"] or not order_data["recipient_phone"] or not order_data["address"]:
#             return Response(
#                 {"error": "Ім’я, телефон і адреса отримувача обов’язкові"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         with transaction.atomic():
#             order = Order.objects.create(**order_data)
#             total_discount = Decimal('0.00')
#             items_data = []

#             for cart_item in cart_items:
#                 subproduct = cart_item.product
#                 # Перевіряємо, чи існує SubProducts
#                 if not SubProducts.objects.filter(id=subproduct.id).exists():
#                     continue

#                 item_price = get_discounted_price(user, subproduct)['new_price']
#                 item_total = item_price * cart_item.quantity

#                 items_data.append(
#                     OrderItem(
#                         order=order,
#                         product=subproduct,
#                         quantity=cart_item.quantity,
#                         product_price=item_price,
#                         total_price=item_total,
#                     )
#                 )

#             if not items_data:
#                 order.delete()
#                 return Response(
#                     {"error": "Жоден товар у кошику не доступний"},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#             OrderItem.objects.bulk_create(items_data)
#             order.calculate_total()
#             cart_items.delete()

#         serializer = OrderSerializer(order)
#         return Response(serializer.data, status=status.HTTP_201_CREATED)

#     @extend_schema(
#         request=OrderSerializer,
#         responses={201: OrderSerializer},
#         description="Створити замовлення вручну, вказавши товари",
#     )
#     @action(detail=False, methods=["post"], url_path="create-manual")
#     def create_manual(self, request):
#         user = request.user if request.user.is_authenticated else None

#         # Перевірка профілю
#         if user:
#             try:
#                 profile = user.profile
#                 if not profile.phone or not profile.address:
#                     return Response(
#                         {"error": "Заповніть профіль (телефон і адресу)"},
#                         status=status.HTTP_400_BAD_REQUEST
#                     )
#             except UserProfile.DoesNotExist:
#                 return Response(
#                     {"error": "Профіль не знайдено"},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         order_data = {
#             "user": user,
#             "payment_method": serializer.validated_data.get("payment_method", "cash"),
#             "delivery_method": serializer.validated_data.get("delivery_method", "pickup"),
#             "recipient_name": serializer.validated_data.get("recipient_name"),
#             "recipient_phone": serializer.validated_data.get("recipient_phone"),
#             "address": profile.address if user else serializer.validated_data.get("address"),
#             "coupon": serializer.validated_data.get("coupon"),
#             "call_me": serializer.validated_data.get("call_me", False),
#         }

#         if not order_data["recipient_name"] or not order_data["recipient_phone"] or not order_data["address"]:
#             return Response(
#                 {"error": "Ім’я, телефон і адреса отримувача обов’язкові"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         manual_items = serializer.validated_data.get("manual_items", [])
#         if not manual_items:
#             return Response(
#                 {"error": "Потрібно вказати товари для замовлення"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         with transaction.atomic():
#             order = Order.objects.create(**order_data)
#             total_discount = Decimal('0.00')
#             items_data = []

#             for item in manual_items:
#                 subproduct = item.get("product")  # Змінено з product_id на product
#                 quantity = item.get("quantity", 1)
#                 if not SubProducts.objects.filter(id=subproduct.id).exists():
#                     continue

#                 item_price = get_discounted_price(user, subproduct)['new_price']
#                 item_total = item_price * quantity

#                 items_data.append(
#                     OrderItem(
#                         order=order,
#                         product=subproduct,
#                         quantity=quantity,
#                         product_price=item_price,
#                         total_price=item_total,
#                     )
#                 )

#             if not items_data:
#                 order.delete()
#                 return Response(
#                     {"error": "Жоден товар не доступний"},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#             OrderItem.objects.bulk_create(items_data)
#             order.calculate_total()

#         serializer = OrderSerializer(order)
#         return Response(serializer.data, status=status.HTTP_201_CREATED)

#     def get_applicable_discount(self, user, subproduct, coupon_code):
#         discount_data = get_discounted_price(user, subproduct)
#         return discount_data['discount_applied']

# from django.db import transaction
# from rest_framework import viewsets, status
# from rest_framework.response import Response
# from rest_framework.decorators import action
# from drf_spectacular.utils import extend_schema
# from .models import Order, OrderItem
# from rest_framework.views import APIView
# from cart.models import Cart
# from .serializers import OrderSerializer, OrderItemSerializer

# from discounts.models import (
#     PromoCode,
#     Coupon,
#     BirthdayDiscount,
#     PersonalDiscount,
#     BonusAccount,
# )
# from django.db import transaction
# from rest_framework import viewsets, status
# from rest_framework.response import Response
# from rest_framework.decorators import action
# from drf_spectacular.utils import extend_schema
# from .models import Order, OrderItem
# from cart.models import Cart

# from product.models import Product, SubProducts
# from .serializers import OrderSerializer, OrderItemSerializer
# from discounts.models import (
#     PromoCode,
#     Coupon,
#     BirthdayDiscount,
#     PersonalDiscount,
#     ProductDiscount
    
# )
# from django.db import transaction
# from rest_framework import viewsets, status
# from rest_framework.response import Response
# from rest_framework.decorators import action
# from drf_spectacular.utils import extend_schema
# from .models import Order, OrderItem
# from cart.models import Cart
# from product.models import SubProducts
# from .serializers import OrderSerializer, OrderItemSerializer
# from discounts.models import PromoCode, Coupon, BirthdayDiscount, PersonalDiscount, ProductDiscount
# from product.utils import get_discounted_price
# from users.models import UserProfile

# class OrderViewSet(viewsets.ModelViewSet):
#     queryset = Order.objects.all()
#     serializer_class = OrderSerializer

#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user if self.request.user.is_authenticated else None)

#     @extend_schema(
#         request=OrderSerializer,
#         responses={201: OrderSerializer},
#         description="Створити замовлення з корзини користувача з урахуванням знижок",
#     )
#     @action(detail=False, methods=["post"], url_path="create-from-cart")
#     def create_from_cart(self, request):
#         user = request.user if request.user.is_authenticated else None
#         session_key = request.session.session_key if not user else None

#         # Перевірка профілю
#         if user:
#             try:
#                 profile = user.profile
#                 if not profile.phone or not profile.address:
#                     return Response(
#                         {"error": "Заповніть профіль (телефон і адресу)"},
#                         status=status.HTTP_400_BAD_REQUEST
#                     )
#             except UserProfile.DoesNotExist:
#                 return Response(
#                     {"error": "Профіль не знайдено"},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#         # Отримуємо кошик
#         if user:
#             cart_items = Cart.objects.filter(user=user)
#         else:
#             if not session_key:
#                 return Response(
#                     {"error": "Сесія не знайдена"}, 
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
#             cart_items = Cart.objects.filter(session_key=session_key)

#         if not cart_items.exists():
#             return Response(
#                 {"error": "Корзина порожня"}, 
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         # Дані замовлення
#         order_data = {
#             "user": user,
#             "payment_method": request.data.get("payment_method", "cash"),
#             "delivery_method": request.data.get("delivery_method", "pickup"),
#             "recipient_name": request.data.get("recipient_name"),
#             "recipient_phone": request.data.get("recipient_phone"),
#             "address": profile.address if user else request.data.get("address"),
#             "coupon": request.data.get("coupon"),
#             "call_me": request.data.get("call_me", False),
#         }

#         if not order_data["recipient_name"] or not order_data["recipient_phone"] or not order_data["address"]:
#             return Response(
#                 {"error": "Ім’я, телефон і адреса отримувача обов’язкові"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         with transaction.atomic():
#             order = Order.objects.create(**order_data)
#             total_discount = Decimal('0.00')
#             items_data = []

#             for cart_item in cart_items:
#                 subproduct = cart_item.product
#                 item_price = get_discounted_price(user, subproduct)['new_price']
#                 item_total = item_price * cart_item.quantity

#                 items_data.append(
#                     OrderItem(
#                         order=order,
#                         product=subproduct,  # Використовуємо SubProducts
#                         quantity=cart_item.quantity,
#                         product_price=item_price,
#                         total_price=item_total,
#                     )
#                 )

#             OrderItem.objects.bulk_create(items_data)
#             order.calculate_total()  # Застосовуємо знижку за великі суми
#             cart_items.delete()

#         serializer = OrderSerializer(order)
#         return Response(serializer.data, status=status.HTTP_201_CREATED)

#     @extend_schema(
#         request=OrderSerializer,
#         responses={201: OrderSerializer},
#         description="Створити замовлення вручну, вказавши товари",
#     )
#     @action(detail=False, methods=["post"], url_path="create-manual")
#     def create_manual(self, request):
#         user = request.user if request.user.is_authenticated else None

#         # Перевірка профілю
#         if user:
#             try:
#                 profile = user.profile
#                 if not profile.phone or not profile.address:
#                     return Response(
#                         {"error": "Заповніть профіль (телефон і адресу)"},
#                         status=status.HTTP_400_BAD_REQUEST
#                     )
#             except UserProfile.DoesNotExist:
#                 return Response(
#                     {"error": "Профіль не знайдено"},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         order_data = {
#             "user": user,
#             "payment_method": serializer.validated_data.get("payment_method", "cash"),
#             "delivery_method": serializer.validated_data.get("delivery_method", "pickup"),
#             "recipient_name": serializer.validated_data.get("recipient_name"),
#             "recipient_phone": serializer.validated_data.get("recipient_phone"),
#             "address": profile.address if user else serializer.validated_data.get("address"),
#             "coupon": serializer.validated_data.get("coupon"),
#             "call_me": serializer.validated_data.get("call_me", False),
#         }

#         if not order_data["recipient_name"] or not order_data["recipient_phone"] or not order_data["address"]:
#             return Response(
#                 {"error": "Ім’я, телефон і адреса отримувача обов’язкові"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         manual_items = serializer.validated_data.get("manual_items", [])
#         if not manual_items:
#             return Response(
#                 {"error": "Потрібно вказати товари для замовлення"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         with transaction.atomic():
#             order = Order.objects.create(**order_data)
#             total_discount = Decimal('0.00')
#             items_data = []

#             for item in manual_items:
#                 subproduct_id = item.get("subproduct")  # Змінено на subproduct
#                 quantity = item.get("quantity", 1)
#                 try:
#                     subproduct = SubProducts.objects.get(id=subproduct_id)
#                 except SubProducts.DoesNotExist:
#                     return Response(
#                         {"error": f"Товар з ID {subproduct_id} не знайдено"},
#                         status=status.HTTP_400_BAD_REQUEST
#                     )

#                 item_price = get_discounted_price(user, subproduct)['new_price']
#                 item_total = item_price * quantity

#                 items_data.append(
#                     OrderItem(
#                         order=order,
#                         product=subproduct,
#                         quantity=quantity,
#                         product_price=item_price,
#                         total_price=item_total,
#                     )
#                 )

#             OrderItem.objects.bulk_create(items_data)
#             order.calculate_total()

#         serializer = OrderSerializer(order)
#         return Response(serializer.data, status=status.HTTP_201_CREATED)

#     def get_applicable_discount(self, user, subproduct, coupon_code):
#         # Використовуємо get_discounted_price замість дублювання логіки
#         discount_data = get_discounted_price(user, subproduct)
#         return discount_data['discount_applied']

# # class OrderViewSet(viewsets.ModelViewSet):
# #     queryset = Order.objects.all()
# #     serializer_class = OrderSerializer

# #     @extend_schema(
# #         request=OrderSerializer,
# #         responses={201: OrderSerializer},
# #         description="Створити замовлення з корзини користувача з урахуванням знижок",
# #     )
# #     @action(detail=False, methods=["post"], url_path="create-from-cart")
# #     def create_from_cart(self, request):
# #         user = request.user if request.user.is_authenticated else None
# #         session_key = request.session.session_key if not user else None

# #         if user:
# #             cart_items = Cart.objects.filter(user=user)
# #         else:
# #             if not session_key:
# #                 return Response(
# #                     {"error": "Сесія не знайдена"}, status=status.HTTP_400_BAD_REQUEST
# #                 )
# #             cart_items = Cart.objects.filter(session_key=session_key)

# #         if not cart_items.exists():
# #             return Response(
# #                 {"error": "Корзина порожня"}, status=status.HTTP_400_BAD_REQUEST
# #             )

# #         order_data = {
# #             "user": user,
# #             "payment_method": request.data.get("payment_method", "cash"),
# #             "delivery_method": request.data.get("delivery_method", "pickup"),
# #             "recipient_name": request.data.get("recipient_name"),
# #             "recipient_phone": request.data.get("recipient_phone"),
# #             "coupon": request.data.get("coupon"),
# #             "call_me": request.data.get("call_me", False),
# #         }

# #         if not order_data["recipient_name"] or not order_data["recipient_phone"]:
# #             return Response(
# #                 {"error": "Ім’я та телефон отримувача обов’язкові"},
# #                 status=status.HTTP_400_BAD_REQUEST,
# #             )

# #         with transaction.atomic():
# #             order = Order.objects.create(**order_data)
# #             total_discount = 0
# #             items_data = []

# #             for cart_item in cart_items:
# #                 product = cart_item.product.parent_product
# #                 item_price = cart_item.product.price
# #                 item_total = cart_item.products_price()

# #                 discount_percentage = self.get_applicable_discount(
# #                     user, product, order_data["coupon"]
# #                 )
# #                 if discount_percentage > 0:
# #                     discount_amount = item_total * (discount_percentage / 100)
# #                     item_total -= discount_amount
# #                     total_discount += discount_amount

# #                 items_data.append(
# #                     OrderItem(
# #                         order=order,
# #                         product=product,
# #                         quantity=cart_item.quantity,
# #                         product_price=cart_item.product.price,
# #                         total_price=item_total,
# #                     )
# #                 )

# #             OrderItem.objects.bulk_create(items_data)
# #             order.discount = total_discount
# #             order.calculate_total()
# #             cart_items.delete()

# #         serializer = OrderSerializer(order)
# #         return Response(serializer.data, status=status.HTTP_201_CREATED)

# #     @extend_schema(
# #         request=OrderSerializer,
# #         responses={201: OrderSerializer},
# #         description="Створити замовлення вручну, вказавши товари",
# #     )
# #     @action(detail=False, methods=["post"], url_path="create-manual")
# #     def create_manual(self, request):
# #         user = request.user if request.user.is_authenticated else None

# #         # Отримуємо дані з запиту
# #         serializer = self.get_serializer(data=request.data)
# #         serializer.is_valid(raise_exception=True)
# #         order_data = {
# #             "user": user,
# #             "payment_method": serializer.validated_data.get("payment_method", "cash"),
# #             "delivery_method": serializer.validated_data.get(
# #                 "delivery_method", "pickup"
# #             ),
# #             "recipient_name": serializer.validated_data.get("recipient_name"),
# #             "recipient_phone": serializer.validated_data.get("recipient_phone"),
# #             "coupon": serializer.validated_data.get("coupon"),
# #             "call_me": serializer.validated_data.get("call_me", False),
# #         }

# #         if not order_data["recipient_name"] or not order_data["recipient_phone"]:
# #             return Response(
# #                 {"error": "Ім’я та телефон отримувача обов’язкові"},
# #                 status=status.HTTP_400_BAD_REQUEST,
# #             )

# #         manual_items = serializer.validated_data.get("manual_items", [])
# #         if not manual_items:
# #             return Response(
# #                 {"error": "Потрібно вказати товари для замовлення"},
# #                 status=status.HTTP_400_BAD_REQUEST,
# #             )

# #         with transaction.atomic():
# #             order = Order.objects.create(**order_data)
# #             total_discount = 0
# #             items_data = []

# #             for item in manual_items:
# #                 product_id = item.get("product")
# #                 quantity = item.get("quantity", 1)
# #                 try:
# #                     product = Product.objects.get(id=product_id)
# #                 except Product.DoesNotExist:
# #                     return Response(
# #                         {"error": f"Товар з ID {product_id} не знайдено"},
# #                         status=status.HTTP_400_BAD_REQUEST,
# #                     )

# #                 item_price = product.price  # Припускаємо, що у Product є поле price
# #                 item_total = item_price * quantity

# #                 discount_percentage = self.get_applicable_discount(
# #                     user, product, order_data["coupon"]
# #                 )
# #                 if discount_percentage > 0:
# #                     discount_amount = item_total * (discount_percentage / 100)
# #                     item_total -= discount_amount
# #                     total_discount += discount_amount

# #                 items_data.append(
# #                     OrderItem(
# #                         order=order,
# #                         product=product,
# #                         quantity=quantity,
# #                         product_price=item_price,
# #                         total_price=item_total,
# #                     )
# #                 )

# #             OrderItem.objects.bulk_create(items_data)
# #             order.discount = total_discount
# #             order.calculate_total()

# #         serializer = OrderSerializer(order)
# #         return Response(serializer.data, status=status.HTTP_201_CREATED)

# #     def get_applicable_discount(self, user, product, coupon_code):
# #         max_discount = 0

# #         if coupon_code:
# #             promo = PromoCode.objects.filter(code=coupon_code).first()
# #             if promo and promo.is_valid():
# #                 if (
# #                     (
# #                         not promo.applicable_products.exists()
# #                         and not promo.applicable_categories.exists()
# #                     )
# #                     or (product in promo.applicable_products.all())
# #                     or (product.category in promo.applicable_categories.all())
# #                 ):
# #                     max_discount = max(max_discount, promo.discount_percentage)
# #                     promo.use()

# #         if user:
# #             coupon = Coupon.objects.filter(user=user, is_active=True).first()
# #             if coupon and coupon.is_valid():
# #                 max_discount = max(max_discount, coupon.discount_percentage)

# #             birthday_discount = BirthdayDiscount.objects.filter(user=user).first()
# #             if birthday_discount and birthday_discount.is_valid():
# #                 max_discount = max(max_discount, birthday_discount.discount_percentage)

# #             personal = PersonalDiscount.objects.filter(
# #                 user=user, is_active=True
# #             ).first()
# #             if personal and personal.is_valid():
# #                 if (
# #                     (
# #                         not personal.applicable_products.exists()
# #                         and not personal.applicable_categories.exists()
# #                     )
# #                     or (product in personal.applicable_products.all())
# #                     or (product.category in personal.applicable_categories.all())
# #                 ):
# #                     max_discount = max(max_discount, personal.discount_percentage)

# #         product_discount = ProductDiscount.objects.filter(
# #             product=product, is_active=True
# #         ).first()
# #         if product_discount and product_discount.is_valid():
# #             max_discount = max(max_discount, product_discount.discount_percentage)

# #         return max_discount


