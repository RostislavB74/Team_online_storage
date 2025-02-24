from rest_framework.decorators import action
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from django.utils.timezone import now
from order.models import Order
from cart.models import Cart
from .serializers import CartSerializer
from order.serializers import OrderSerializer
from django.shortcuts import get_object_or_404

class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Фільтрує кошик лише для поточного користувача"""
        return Cart.objects.filter(user=self.request.user)
    @action(detail=False, methods=["post"])
    def create_order(self, request):
        """Створює передзамовлення на основі кошика"""
        cart = get_object_or_404(Cart, user=request.user)

        if not cart.items.exists():
            return Response({"error": "Кошик порожній"}, status=status.HTTP_400_BAD_REQUEST)

        # Передаємо `user` як об'єкт і загальну вартість
        data = {"user": request.user, "total_price": cart.total_price}
        serializer = OrderSerializer(data=data, context={"request": request})

        if serializer.is_valid():
            order = serializer.save()
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # @action(detail=False, methods=['post'])
    # def create_order(self, request):
    #     """Створює передзамовлення на основі кошика"""
    #     cart = get_object_or_404(Cart, user=request.user)  # Безпечний доступ до кошика

    #     if not cart.items.exists():
    #         return Response({"error": "Кошик порожній"}, status=status.HTTP_400_BAD_REQUEST)

    #     data = {"user": request.user}  # Передаємо об'єкт користувача
    #     serializer = OrderSerializer(data=data, context={"request": request})

    #     if serializer.is_valid():
    #         order = serializer.save()
    #         return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
        
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# from django.shortcuts import render

# # Create your views here.
# from rest_framework import viewsets, status
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from .models import Cart, CartItem
# from order.models import Order, OrderItem
# from .serializers import CartSerializer, CartItemSerializer
# from order.serializers import OrderSerializer
# from product.models import Product
# from rest_framework.decorators import action
# from rest_framework import permissions
# from rest_framework.decorators import action
# from rest_framework import viewsets, status
# from rest_framework.response import Response
# from django.utils.timezone import now
# from order.models import Order
# from order.serializers import OrderSerializer

# class CartViewSet(viewsets.ModelViewSet):
#     queryset = Cart.objects.all()
#     serializer_class = CartSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     @action(detail=False, methods=['post'])
#     def create_order(self, request):
#         """Створює передзамовлення на основі кошика"""
#         cart = request.user.cart
#         if not cart.items.exists():
#             return Response({"error": "Кошик порожній"}, status=status.HTTP_400_BAD_REQUEST)

#         data = {"user": request.user.id}  # Передаємо лише користувача, решта автоматично підтягнеться
#         serializer = OrderSerializer(data=data, context={"request": request})

#         if serializer.is_valid():
#             order = serializer.save()
#             return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
        
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class CartViewSet(viewsets.ModelViewSet):
#     queryset = Cart.objects.all()
#     serializer_class = CartSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     @action(detail=False, methods=['post'])
#     def create_order(self, request):
#         cart = request.user.cart
#         if not cart.items.exists():
#             return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

#         order = Order.objects.create(user=request.user)
#         for item in cart.items.all():
#             OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)
#         cart.items.all().delete()

#         return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
# from rest_framework.decorators import action
# from rest_framework import viewsets, status
# from rest_framework.response import Response
# from django.utils.timezone import now

# class CartViewSet(viewsets.ModelViewSet):
#     queryset = Cart.objects.all()
#     serializer_class = CartSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     @action(detail=False, methods=['post'])
#     def create_order(self, request):
#         cart = request.user.cart

#         if not cart.items.exists():
#             return Response({"error": "Кошик порожній"}, status=status.HTTP_400_BAD_REQUEST)

#         # Створюємо нове замовлення
#         order = Order.objects.create(user=request.user, status="pending", created_at=now())

#         # Додаємо товари з кошика до замовлення
#         for item in cart.items.all():
#             OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)

#         # Очищаємо кошик після створення замовлення
#         cart.items.all().delete()

#         return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


# class CartViewSet(viewsets.ViewSet):
#     permission_classes = [IsAuthenticated]

#     def list(self, request):
#         cart, created = Cart.objects.get_or_create(user=request.user)
#         serializer = CartSerializer(cart)
#         return Response(serializer.data)

#     def add_item(self, request):
#         user_cart, _ = Cart.objects.get_or_create(user=request.user)
#         product_id = request.data.get("product_id")
#         quantity = request.data.get("quantity", 1)

#         try:
#             product = Product.objects.get(id=product_id)
#         except Product.DoesNotExist:
#             return Response({"error": "Товар не знайдено"}, status=status.HTTP_404_NOT_FOUND)

#         cart_item, created = CartItem.objects.get_or_create(cart=user_cart, product=product)
#         if not created:
#             cart_item.quantity += int(quantity)
#             cart_item.save()

#         return Response({"message": "Товар додано до кошика"}, status=status.HTTP_201_CREATED)

#     def remove_item(self, request, pk):
#         try:
#             cart_item = CartItem.objects.get(id=pk, cart__user=request.user)
#             cart_item.delete()
#             return Response({"message": "Товар видалено з кошика"}, status=status.HTTP_204_NO_CONTENT)
#         except CartItem.DoesNotExist:
#             return Response({"error": "Товар не знайдено у кошику"}, status=status.HTTP_404_NOT_FOUND)

#     def clear_cart(self, request):
#         user_cart = Cart.objects.filter(user=request.user).first()
#         if user_cart:
#             user_cart.items.all().delete()
#         return Response({"message": "Кошик очищено"}, status=status.HTTP_204_NO_CONTENT)
