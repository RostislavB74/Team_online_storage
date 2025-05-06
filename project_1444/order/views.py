import logging
from decimal import Decimal

from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from order.tasks import send_order_confirmation_email
from order.models import Order, OrderItem
from cart.models import Cart
from product.models import SubProducts
from order.serializers import OrderSerializer, OrderCreateSerializer
from product.utils import get_discounted_price
from users.models import UserProfile
from discounts.models import BirthdayDiscount

logger = logging.getLogger(__name__)


class CreateOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            # Створюємо замовлення
            order = serializer.save(user=user)

            # Обчислюємо total_price
            total_price = Decimal("0.00")
            for item in order.items.all():
                total_price += Decimal(item.quantity) * Decimal(item.product_price)
            order.total_price = total_price

            # Перевіряємо, чи є застосована BirthdayDiscount у сесії
            discount_amount = Decimal("0.00")
            birthday_discount_id = request.session.get("applied_birthday_discount")
            if birthday_discount_id:
                try:
                    birthday_discount = BirthdayDiscount.objects.get(
                        id=birthday_discount_id
                    )
                    discount_percentage = Decimal(birthday_discount.discount_percentage)
                    discount_amount = (total_price * discount_percentage) / Decimal(
                        "100.0"
                    )
                    order.birthday_discount = birthday_discount
                except BirthdayDiscount.DoesNotExist:
                    pass

            # Враховуємо знижку
            order.discount = discount_amount
            order.final_price = total_price - discount_amount
            order.save()

            # Очищаємо сесію
            request.session.pop("applied_birthday_discount", None)

            response_serializer = OrderSerializer(order)
            return Response(
                {
                    "payment_url": f"/api/payment/pay/{order.id}/",
                    "order": response_serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class CreateOrderAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         user = request.user
#         serializer = OrderSerializer(data=request.data)
#         if serializer.is_valid():
#             # Створюємо замовлення
#             order = serializer.save(user=user)

#             # Обчислюємо total_price на основі товарів
#             total_price = Decimal('0.00')
#             for item in order.items.all():
#                 total_price += Decimal(item.quantity) * Decimal(item.product_price)
#             order.total_price = total_price

#             # Перевіряємо, чи є доступна BirthdayDiscount
#             discount_amount = Decimal('0.00')
#             birthday_discount = None
#             if hasattr(user, 'profile'):
#                 birthday_qs = BirthdayDiscount.objects.filter(
#                     profile__user=user,
#                     used_year__isnull=True
#                 )
#                 for bd in birthday_qs:
#                     if bd.is_valid:
#                         birthday_discount = bd
#                         break

#             # Застосовуємо BirthdayDiscount, якщо є
#             if birthday_discount:
#                 discount_percentage = Decimal(birthday_discount.discount_percentage)
#                 discount_amount = (total_price * discount_percentage) / Decimal('100.0')
#                 birthday_discount.used_year = now().year
#                 birthday_discount.save()

#             # Враховуємо знижку
#             order.discount = discount_amount
#             order.final_price = total_price - discount_amount
#             order.save()

#             # Серіалізуємо і повертаємо відповідь
#             response_serializer = OrderSerializer(order)
#             return Response({
#                 "payment_url": f"/api/payment/pay/{order.id}/",
#                 "order": response_serializer.data
#             }, status=status.HTTP_201_CREATED)


#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user if self.request.user.is_authenticated else None
        )

    @extend_schema(
        request=OrderCreateSerializer,
        responses={201: OrderSerializer},
        description=_("Створити замовлення з корзини користувача з урахуванням знижок"),
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
                logger.info(
                    f"User profile: phone={profile.phone}, address={profile.address}"
                )
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
                    {"error": _("Сесія не знайдена")},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            cart_items = Cart.objects.filter(session_key=session_key)

        logger.info(f"Cart items count: {cart_items.count()}")
        if not cart_items.exists():
            logger.error("Cart is empty")
            return Response(
                {"error": _("Корзина порожня")}, status=status.HTTP_400_BAD_REQUEST
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
            "discount": order_data.get("discount", Decimal("0.00")),
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
                item_price = discounted["new_price"]
                item_total = item_price * cart_item.quantity
                logger.info(
                    f"Subproduct: {subproduct}, Price: {item_price}, Total: {item_total}"
                )

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
                    {"error": _("Жоден товар у кошику не доступний")},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            OrderItem.objects.bulk_create(items_data)
            logger.info(f"Created {len(items_data)} order items")
            order.calculate_total()  # Обчислюємо total_price і final_price
            logger.info(
                f"Order total_price: {order.total_price}, final_price: {order.final_price}"
            )
            cart_items.delete()

            # Якщо обрано LiqPay або GooglePay, повертаємо URL для оплати
            if order_data_dict["payment_method"] in ["liqpay", "googlepay"]:
                payment_url = f"/api/payment/pay/{order.id}/"
                logger.info(f"Returning payment URL: {payment_url}")
                return Response(
                    {
                        "payment_url": payment_url,
                        "order": OrderSerializer(
                            order, context={"request": request}
                        ).data,
                    },
                    status=status.HTTP_201_CREATED,
                )

            # Відправка email для інших методів оплати
            if order.user and order.user.email:
                logger.info(f"Sending order confirmation email to {order.user.email}")
                send_order_confirmation_email.delay(order.id, order.user.email)

        serializer = OrderSerializer(order, context={"request": request})
        logger.info("Order created successfully")
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UpdateOrderStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": [
                            "awaiting_payment",
                            "paid",
                            "shipped",
                            "delivered",
                            "failed",
                            "reversed",
                            "cancelled",
                        ],
                    },
                    "payment_status": {
                        "type": "string",
                        "enum": ["success", "failed", "reversed"],
                        "nullable": True,
                    },
                },
                "required": ["status"],
            }
        },
        responses={
            200: {"type": "object", "properties": {"message": {"type": "string"}}},
            400: {"type": "object", "properties": {"error": {"type": "string"}}},
            404: {"type": "object", "properties": {"error": {"type": "string"}}},
        },
        description=_("Update the status of an order with optional payment status."),
    )
    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user)
            new_status = request.data.get("status")
            payment_status = request.data.get("payment_status")
            order.update_status(new_status, payment_status)
            return Response(
                {
                    "message": _("Order #{} status updated to {}").fromat(
                        order_id, new_status
                    )
                },
                status=status.HTTP_200_OK,
            )
        except Order.DoesNotExist:
            return Response(
                {"error": _("Order not found or access denied")},
                status=status.HTTP_404_NOT_FOUND,
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # order/views.py


class LiqPayCallbackAPIView(APIView):
    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "integer"},
                    "status": {
                        "type": "string",
                        "enum": ["success", "failure", "reversed"],
                    },
                },
                "required": ["order_id", "status"],
            }
        },
        responses={
            200: {"type": "object", "properties": {"message": {"type": "string"}}},
            400: {"type": "object", "properties": {"error": {"type": "string"}}},
        },
        description=_("Handle LiqPay payment callback."),
    )
    def post(self, request):
        order_id = request.data.get("order_id")
        payment_status = request.data.get("status")

        try:
            order = Order.objects.get(id=order_id)
            if order.status != "awaiting_payment":
                return Response(
                    {"error": _("Order is not awaiting payment")},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if payment_status == "success":
                order.update_status("paid", payment_status="success")
                if order.status == "in_transit":
                    return Response(
                        {
                            "message": _(
                                "Order #{} paid, awaiting stock replenishment"
                            ).format(order_id)
                        },
                        status=status.HTTP_200_OK,
                    )
            elif payment_status == "failure":
                order.update_status("failed", payment_status="failed")
            elif payment_status == "reversed":
                order.update_status("reversed", payment_status="reversed")
            else:
                return Response(
                    {"error": _("Invalid payment status")},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(
                {"message": _("Order #{} payment status updated").format(order_id)},
                status=status.HTTP_200_OK,
            )
        except Order.DoesNotExist:
            return Response(
                {"error": _("Order not found")}, status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
