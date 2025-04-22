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
