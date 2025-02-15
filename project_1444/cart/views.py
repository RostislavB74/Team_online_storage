from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from product.models import Product

class CartViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def add_item(self, request):
        user_cart, _ = Cart.objects.get_or_create(user=request.user)
        product_id = request.data.get("product_id")
        quantity = request.data.get("quantity", 1)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Товар не знайдено"}, status=status.HTTP_404_NOT_FOUND)

        cart_item, created = CartItem.objects.get_or_create(cart=user_cart, product=product)
        if not created:
            cart_item.quantity += int(quantity)
            cart_item.save()

        return Response({"message": "Товар додано до кошика"}, status=status.HTTP_201_CREATED)

    def remove_item(self, request, pk):
        try:
            cart_item = CartItem.objects.get(id=pk, cart__user=request.user)
            cart_item.delete()
            return Response({"message": "Товар видалено з кошика"}, status=status.HTTP_204_NO_CONTENT)
        except CartItem.DoesNotExist:
            return Response({"error": "Товар не знайдено у кошику"}, status=status.HTTP_404_NOT_FOUND)

    def clear_cart(self, request):
        user_cart = Cart.objects.filter(user=request.user).first()
        if user_cart:
            user_cart.items.all().delete()
        return Response({"message": "Кошик очищено"}, status=status.HTTP_204_NO_CONTENT)
