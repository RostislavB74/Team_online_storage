
from rest_framework import generics, permissions
from rest_framework import viewsets, status

from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderItemSerializer


from cart.models import Cart, CartItem
from product.models import Product





class CreateOrderFromCartView(APIView):
    def post(self, request):
        user = request.user
        try:
            cart = Cart.objects.get(user=user)
            cart_items = CartItem.objects.filter(cart=cart)
            

            # Підготовка даних для нового замовлення
            order_data = {
                'user': user.id,
                # Додайте інші поля, які мають бути заповнені або мають значення за замовчуванням
                'items': [{'product': item.product_id, 'quantity': item.quantity, 'total_price': item.total_price} for item in cart_items]
         # Початкова ціна без урахування знижок
            }

            # Додаткові дані можуть бути передані в запиті
            order_data.update(request.data)

            serializer = OrderSerializer(data=order_data)
            if serializer.is_valid():
                order = serializer.save()
                
                # Очистити корзину після створення замовлення
                cart_items.delete()
                
                # Резервування товарів на складах (псевдокод)
                # for item in order.items.all():
                #     item.product.reserve_stock(item.quantity)
                
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Cart.DoesNotExist:
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
        



class CreateOrderView(generics.CreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]  # Тільки авторизовані користувачі

    def create(self, request, *args, **kwargs):
        user = request.user

        # Отримуємо корзину
        cart = Cart.objects.filter(user=user).first()
        if not cart or not cart.items.exists():
            raise ValidationError("Корзина порожня")

        # Отримуємо додаткові параметри замовлення
        payment_method = request.data.get("payment_method")
        delivery_method = request.data.get("delivery_method")
        comment = request.data.get("comment", "")
        call_me_back = request.data.get("call_me_back", False)
        coupon_code = request.data.get("coupon_code", None)

        # Створюємо замовлення
        order = Order.objects.create(
            user=user,
            payment_method=payment_method,
            delivery_method=delivery_method,
            comment=comment,
            call_me_back=call_me_back,
            total_price=0,  # Підрахуємо нижче
        )

        # Переносимо товари з корзини в замовлення
        total_price = 0
        for cart_item in cart.items.all():
            order_item = OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
            total_price += order_item.price * order_item.quantity

        # Застосовуємо купон, якщо є
        if coupon_code:
            discount_amount = self.apply_coupon(coupon_code, total_price)  # Функція для застосування купону
            total_price -= discount_amount

        # Оновлюємо загальну суму та зберігаємо замовлення
        order.total_price = total_price
        order.save()

        # Очищаємо корзину
        cart.items.all().delete()

        # Відправляємо відповідь
        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def apply_coupon(self, coupon_code, total_price):
        """ Перевіряємо купон і застосовуємо знижку """
        if coupon_code == "DISCOUNT2024":  # Тут має бути логіка перевірки купонів
            return total_price * 0.1  # Наприклад, 10% знижки
        return 0

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    @action(detail=False, methods=["post"])
    def create_order(self, request):
        user = request.user if request.user.is_authenticated else None
        cart = Cart.objects.get(user=user) if user else None

        if not cart or not cart.items.exists():
            return Response({"error": "Корзина порожня"}, status=status.HTTP_400_BAD_REQUEST)

        # Створюємо замовлення
        order = Order.objects.create(
            user=user,
            payment_method=request.data.get("payment_method"),
            delivery_method=request.data.get("delivery_method"),
            coupon=request.data.get("coupon"),
            discount=request.data.get("discount", 0),
            call_me=request.data.get("call_me", False)
        )

        # Копіюємо товари з Cart → OrderItem
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                product_price=cart_item.product_price,
                total_price=cart_item.total_price
            )

        # Оновлюємо фінальну суму
        order.calculate_total()

        # Очищуємо корзину
        cart.clear()

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

# # from rest_framework import viewsets, permissions
# # from rest_framework.response import Response
# # from rest_framework.decorators import action
# # from .models import Order
# # from .serializers import OrderSerializer

# # class OrderViewSet(viewsets.ModelViewSet):
# #     queryset = Order.objects.all().order_by("-created_at")
# #     serializer_class = OrderSerializer
# #     permission_classes = [permissions.IsAuthenticated]

# #     def get_queryset(self):
# #         if self.request.user.is_staff:
# #             return Order.objects.all()
# #         return Order.objects.filter(user=self.request.user)

# #     def perform_create(self, serializer):
# #         serializer.save(user=self.request.user)

# #     @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
# #     def update_status(self, request, pk=None):
# #         order = self.get_object()
# #         new_status = request.data.get("status")
# #         if new_status in dict(Order.STATUS_CHOICES):
# #             order.status = new_status
# #             order.save()
# #             return Response({"status": "updated", "new_status": order.get_status_display()})
# #         return Response({"error": "Invalid status"}, status=400)

# # from rest_framework import viewsets, permissions
# # from rest_framework.response import Response
# # from rest_framework.decorators import action
# # from .models import Order
# # from .serializers import OrderSerializer
# # from rest_framework import viewsets, permissions
# # from rest_framework.response import Response
# # from rest_framework.decorators import action
# # from .models import Order
# # from .serializers import OrderSerializer

# # class OrderViewSet(viewsets.ModelViewSet):
# #     queryset = Order.objects.all().order_by("-created_at")
# #     serializer_class = OrderSerializer
# #     permission_classes = [permissions.IsAuthenticated]

# #     def get_queryset(self):
# #         if self.request.user.is_staff:
# #             return Order.objects.all()
# #         return Order.objects.filter(user=self.request.user)

# #     def perform_create(self, serializer):
# #         serializer.save(user=self.request.user)

# #     @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
# #     def update_status(self, request, pk=None):
# #         order = self.get_object()
# #         new_status = request.data.get("status")
# #         if new_status in dict(Order.STATUS_CHOICES):
# #             order.status = new_status
# #             order.save()
# #             return Response({"status": "updated", "new_status": order.get_status_display()})
# #         return Response({"error": "Invalid status"}, status=400)

# # class OrderViewSet(viewsets.ModelViewSet):
# #     queryset = Order.objects.all().order_by("-created_at")
# #     serializer_class = OrderSerializer
# #     permission_classes = [permissions.IsAuthenticated]

# #     def get_queryset(self):
# #         if self.request.user.is_staff:
# #             return Order.objects.all()
# #         return Order.objects.filter(user=self.request.user)

# #     def perform_create(self, serializer):
# #         serializer.save(user=self.request.user)

# #     @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
# #     def update_status(self, request, pk=None):
# #         order = self.get_object()
# #         new_status = request.data.get("status")
# #         if new_status in dict(Order.STATUS_CHOICES):
# #             order.status = new_status
# #             order.save()
# #             return Response({"status": "updated", "new_status": order.get_status_display()})
# #         return Response({"error": "Invalid status"}, status=400)

# # from django.shortcuts import render
# # from rest_framework import viewsets, permissions
# # from .models import Order, OrderItem
# # from .serializers import OrderSerializer, OrderItemSerializer
# # from rest_framework.decorators import action
# # from rest_framework.response import Response

# # class OrderViewSet(viewsets.ModelViewSet):
# #     queryset = Order.objects.all().order_by("-created_at")
# #     serializer_class = OrderSerializer
# #     permission_classes = [permissions.IsAuthenticated]

# #     def perform_create(self, serializer):
# #         print(self.request.data)  # Подивись, що приходить
# #         serializer.save(user=self.request.user)
   
# #     @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
# #     def update_status(self, request, pk=None):
# #         order = self.get_object()
# #         new_status = request.data.get("status")
# #         if new_status in dict(Order.STATUS_CHOICES):
# #             order.status = new_status
# #             order.save()
# #             return Response({"status": "updated", "new_status": order.get_status_display()})
# #         return Response({"error": "Invalid status"}, status=400)