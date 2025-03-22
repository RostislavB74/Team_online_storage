from rest_framework.response import Response
from rest_framework import viewsets
from .models import Cart
from .serializers import CartSerializer
from rest_framework.response import Response
from rest_framework import viewsets
from .models import Cart
from .serializers import CartSerializer

class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    def list(self, request, *args, **kwargs):
        """Отримання списку корзин + загальної суми"""
        user = request.user

        # Визначаємо корзини користувача
        if user.is_authenticated:
            cart_items = Cart.objects.filter(user=user)
        else:
            session_key = request.session.session_key
            cart_items = Cart.objects.filter(session_key=session_key)

        # Серіалізуємо корзини
        serializer = self.get_serializer(cart_items, many=True)

        # Обчислюємо загальну суму всіх товарів у корзині
        total_sum = sum(item.products_price() for item in cart_items)

        # Формуємо відповідь без дублювання total_sum_carts
        return Response({
            "carts": serializer.data,  # список корзин
            "total_sum_carts": total_sum  # загальна сума всіх корзин
        })
