# from rest_framework.decorators import action
# from rest_framework import viewsets, status, permissions
# from rest_framework.response import Response
# from django.utils.timezone import now
# from order.models import Order
# from cart.models import Cart
# # from .serializers import CartSerializer
# from order.serializers import OrderSerializer
# from django.shortcuts import get_object_or_404
# from drf_spectacular.utils import extend_schema
# from django.http import JsonResponse
# from django.template.loader import render_to_string
# from django.urls import reverse
# from cart.utils import get_user_carts
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Cart
from .serializers import CartSerializer

class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Cart.objects.filter(user=user)
        else:
            session_key = self.request.session.session_key
            return Cart.objects.filter(session_key=session_key)

    @action(detail=False, methods=["get"])
    def total_price(self, request):
        """Отримати загальну суму всіх товарів у корзині"""
        cart_items = self.get_queryset()
        total_price = cart_items.total_price()
        return Response({"total_price": total_price})

# from product.models import SubProducts
# from rest_framework import viewsets, permissions
# from rest_framework.response import Response
# from django.shortcuts import get_object_or_404
# from .models import Cart
# from .serializers import CartSerializer
# from product.models import SubProducts

# class CartViewSet(viewsets.ModelViewSet):
#     serializer_class = CartSerializer
#     permission_classes = [permissions.IsAuthenticated]  # Доступ лише авторизованим користувачам

#     def get_queryset(self):
#         user = self.request.user
#         if user.is_authenticated:
#             return Cart.objects.filter(user=user)
#         else:
#             session_key = self.request.session.session_key
#             return Cart.objects.filter(session_key=session_key)

#     def create(self, request, *args, **kwargs):
#         """Додає товар у корзину або збільшує кількість, якщо він уже там є"""
#         user = request.user if request.user.is_authenticated else None
#         session_key = request.session.session_key or request.session.create()

#         product_id = request.data.get("product")
#         quantity = int(request.data.get("quantity", 1))
#         product = get_object_or_404(SubProducts, id=product_id)

#         cart_item, created = Cart.objects.get_or_create(
#             user=user,
#             session_key=session_key if user is None else None,
#             product=product,
#             defaults={"quantity": quantity},
#         )

#         if not created:
#             cart_item.quantity += quantity
#             cart_item.save()

#         serializer = self.get_serializer(cart_item)
#         return Response(serializer.data)

#     def destroy(self, request, *args, **kwargs):
#         """Видалення товару з корзини"""
#         cart_item = self.get_object()
#         cart_item.delete()
#         return Response({"message": "Товар видалено з корзини"}, status=204)


# def cart_add(request):

#     product_id = request.POST.get("product_id")

#     product = SubProducts.objects.get(id=product_id)
    
#     if request.user.is_authenticated:
#         carts = Cart.objects.filter(user=request.user, product=product)

#         if carts.exists():
#             cart = carts.first()
#             if cart:
#                 cart.quantity += 1
#                 cart.save()
#         else:
#             Cart.objects.create(user=request.user, product=product, quantity=1)

#     else:
#         carts = Cart.objects.filter(
#             session_key=request.session.session_key, product=product)

#         if carts.exists():
#             cart = carts.first()
#             if cart:
#                 cart.quantity += 1
#                 cart.save()
#         else:
#             Cart.objects.create(
#                 session_key=request.session.session_key, product=product, quantity=1)
    
#     user_cart = get_user_carts(request)
#     cart_items_html = render_to_string(
#         "carts/includes/included_cart.html", {"carts": user_cart}, request=request)

#     response_data = {
#         "message": "Товар доданий в корзину",
#         "cart_items_html": cart_items_html,
#     }

#     return JsonResponse(response_data)
            

# def cart_change(request):
#     cart_id = request.POST.get("cart_id")
#     quantity = request.POST.get("quantity")

#     cart = Cart.objects.get(id=cart_id)

#     cart.quantity = quantity
#     cart.save()
#     updated_quantity = cart.quantity

#     user_cart = get_user_carts(request)

#     context = {"carts": user_cart}

#     # if referer page is create_order add key orders: True to context
#     referer = request.META.get('HTTP_REFERER')
#     if reverse('orders:create_order') in referer:
#         context["orders"] = True

#     cart_items_html = render_to_string(
#         "carts/includes/included_cart.html", context, request=request)

#     response_data = {
#         "message": "Количество изменено",
#         "cart_items_html": cart_items_html,
#         "quantity": updated_quantity,
#     }

#     return JsonResponse(response_data)



# def cart_remove(request):
    
#     cart_id = request.POST.get("cart_id")

#     cart = Cart.objects.get(id=cart_id)
#     quantity = cart.quantity
#     cart.delete()

#     user_cart = get_user_carts(request)

#     context = {"carts": user_cart}

#     # if referer page is create_order add key orders: True to context
#     referer = request.META.get('HTTP_REFERER')
#     if reverse('orders:create_order') in referer:
#         context["orders"] = True

#     cart_items_html = render_to_string(
#         "carts/includes/included_cart.html", context, request=request)

#     response_data = {
#         "message": "Товар удален",
#         "cart_items_html": cart_items_html,
#         "quantity_deleted": quantity,
#     }

#     return JsonResponse(response_data)

# # @extend_schema(tags=["Cart API"])
# # class CartViewSet(viewsets.ModelViewSet):
# #     queryset = Cart.objects.all()
# #     serializer_class = CartSerializer
# #     permission_classes = [permissions.IsAuthenticated]

# #     def get_queryset(self):
# #         """Фільтрує кошик лише для поточного користувача"""
# #         return Cart.objects.filter(user=self.request.user)

# #     @action(detail=False, methods=["post"])
# #     def create_order(self, request):
# #         """Створює передзамовлення на основі кошика"""
# #         cart = get_object_or_404(Cart, user=request.user)

# #         if not cart.items.exists():
# #             return Response(
# #                 {"error": "Кошик порожній"}, status=status.HTTP_400_BAD_REQUEST
# #             )

# #         # Передаємо `user` як об'єкт і загальну вартість
# #         data = {"user": request.user, "total_price": cart.total_price}
# #         serializer = OrderSerializer(data=data, context={"request": request})

# #         if serializer.is_valid():
# #             order = serializer.save()
# #             return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

# #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# #     @extend_schema(
# #         summary="Get example data",
# #         description="Returns an example response with some data.",
# #         responses={200: dict},
# #     )
# #     def get(self, request):
# #         return Response({"message": "Hello, API!"})

# #     @action(detail=True, methods=["post"])
# #     def add_item(self, request, pk=None):
# #         """Додає товар у кошик"""
# #         cart = self.get_object()
# #         product_id = request.data.get("product_id")
# #         quantity = request.data.get("quantity", 1)

# #         if not product_id:
# #             return Response(
# #                 {"error": "Product ID is required"}, status=status.HTTP_400_BAD_REQUEST
# #             )

# #         try:
# #             item, created = CartItem.objects.get_or_create(
# #                 cart=cart, product_id=product_id
# #             )
# #             if not created:
# #                 item.quantity += int(quantity)
# #                 item.save()
# #             return Response(
# #                 CartItemSerializer(item).data, status=status.HTTP_201_CREATED
# #             )
# #         except Exception as e:
# #             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
