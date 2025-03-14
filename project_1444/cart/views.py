from rest_framework.decorators import action
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from django.utils.timezone import now
from order.models import Order
from cart.models import Cart
from .serializers import CartSerializer
from order.serializers import OrderSerializer
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema


@extend_schema(tags=["Cart API"])
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
            return Response(
                {"error": "Кошик порожній"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Передаємо `user` як об'єкт і загальну вартість
        data = {"user": request.user, "total_price": cart.total_price}
        serializer = OrderSerializer(data=data, context={"request": request})

        if serializer.is_valid():
            order = serializer.save()
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Get example data",
        description="Returns an example response with some data.",
        responses={200: dict},
    )
    def get(self, request):
        return Response({"message": "Hello, API!"})

    @action(detail=True, methods=["post"])
    def add_item(self, request, pk=None):
        """Додає товар у кошик"""
        cart = self.get_object()
        product_id = request.data.get("product_id")
        quantity = request.data.get("quantity", 1)

        if not product_id:
            return Response(
                {"error": "Product ID is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            item, created = CartItem.objects.get_or_create(
                cart=cart, product_id=product_id
            )
            if not created:
                item.quantity += int(quantity)
                item.save()
            return Response(
                CartItemSerializer(item).data, status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
