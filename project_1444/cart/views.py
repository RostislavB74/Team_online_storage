from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from .models import Cart
from .serializers import CartSerializer
from product.models import SubProducts
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiResponse

class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Cart.objects.filter(user=user)
        session_key = self.request.session.session_key
        if not session_key:
            self.request.session.create()
            session_key = self.request.session.session_key
        return Cart.objects.filter(session_key=session_key)

    @extend_schema(
        responses={
            200: OpenApiResponse(
                response={
                    'type': 'object',
                    'properties': {
                        'carts': {'type': 'array', 'items': {'$ref': '#/components/schemas/Cart'}},
                        'total_sum_carts': {'type': 'number', 'format': 'float'},
                        'total_quantity': {'type': 'integer'}
                    }
                },
                description='Список елементів кошика, загальна сума і кількість'
            )
        }
    )
    def list(self, request, *args, **kwargs):
        """Отримання списку корзин + загальної суми"""
        cart_items = self.get_queryset()
        serializer = self.get_serializer(cart_items, many=True)
        total_sum = cart_items.total_price(user=request.user)
        total_quantity = cart_items.total_quantity()

        return Response({
            "carts": serializer.data,
            "total_sum_carts": float(total_sum),  # Конвертуємо Decimal у float для JSON
            "total_quantity": total_quantity
        })

    @action(detail=False, methods=['post'], url_path='add')
    def add(self, request):
        """Додавання товару до корзини"""
        subproduct_id = request.data.get('subproduct_id')
        quantity = int(request.data.get('quantity', 1))
        subproduct = get_object_or_404(SubProducts, id=subproduct_id)

        session_key = self.request.session.session_key
        if not session_key:
            request.session.create()
            session_key = self.request.session.session_key

        cart, created = Cart.objects.get_or_create(
            user=request.user if request.user.is_authenticated else None,
            session_key=session_key if not request.user.is_authenticated else None,
            product=subproduct,
            defaults={'quantity': quantity}
        )
        if not created:
            cart.quantity += quantity
            cart.save()

        serializer = self.get_serializer(cart)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'], url_path='remove')
    def remove(self, request, pk=None):
        """Видалення товару з корзини"""
        cart = get_object_or_404(Cart, pk=pk)
        cart.delete()
        return Response({"message": "Товар видалено з корзини"}, status=status.HTTP_204_NO_CONTENT)


# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from django.db import transaction
# from django.core.mail import send_mail
# from .models import Cart
# from order.models import Order, OrderItem
# from product.models import SubProducts
# from product.utils import get_discounted_price
# from decimal import Decimal
# from rest_framework.response import Response
# from rest_framework import viewsets
# from rest_framework.permissions import IsAuthenticatedOrReadOnly
# from .serializers import CartSerializer
# from rest_framework.decorators import action

# class CartViewSet(viewsets.ModelViewSet):
#     queryset = Cart.objects.all()
#     serializer_class = CartSerializer
#     permission_classes = [IsAuthenticatedOrReadOnly]

#     def get_queryset(self):
#         user = self.request.user
#         if user.is_authenticated:
#             return Cart.objects.filter(user=user)
#         session_key = self.request.session.session_key
#         if not session_key:
#             self.request.session.create()
#             session_key = self.request.session.session_key
#         return Cart.objects.filter(session_key=session_key)

#     def list(self, request, *args, **kwargs):
#         """Отримання списку корзин + загальної суми"""
#         cart_items = self.get_queryset()
#         serializer = self.get_serializer(cart_items, many=True)
#         total_sum = cart_items.total_price(user=request.user)
#         total_quantity = cart_items.total_quantity()

#         return Response({
#             "carts": serializer.data,
#             "total_sum_carts": total_sum,
#             "total_quantity": total_quantity
#         })

#     @action(detail=False, methods=['post'])
#     def add(self, request):
#         """Додавання товару до корзини"""
#         subproduct_id = request.data.get('subproduct_id')
#         quantity = int(request.data.get('quantity', 1))
#         subproduct = get_object_or_404(SubProducts, id=subproduct_id)

#         session_key = request.session.session_key
#         if not session_key:
#             request.session.create()
#             session_key = request.session.session_key

#         cart, created = Cart.objects.get_or_create(
#             user=request.user if request.user.is_authenticated else None,
#             session_key=session_key if not request.user.is_authenticated else None,
#             product=subproduct,
#             defaults={'quantity': quantity}
#         )
#         if not created:
#             cart.quantity += quantity
#             cart.save()

#         serializer = self.get_serializer(cart)
#         return Response(serializer.data)

#     @action(detail=True, methods=['delete'])
#     def remove(self, request, pk=None):
#         """Видалення товару з корзини"""
#         cart = get_object_or_404(Cart, pk=pk)
#         cart.delete()
#         return Response({"message": "Товар видалено з корзини"})
# def add_to_cart(request, subproduct_id):
#     subproduct = get_object_or_404(SubProducts, id=subproduct_id)
#     session_key = request.session.session_key
#     if not session_key:
#         request.session.create()
#         session_key = request.session.session_key

#     cart, created = Cart.objects.get_or_create(
#         user=request.user if request.user.is_authenticated else None,
#         session_key=session_key if not request.user.is_authenticated else None,
#         product=subproduct,
#         defaults={'quantity': 1}
#     )
#     if not created:
#         cart.quantity += 1
#         cart.save()

#     messages.success(request, f"{subproduct} додано до кошика.")
#     return redirect('cart_view')

# def cart_view(request):
#     cart_items = Cart.objects.filter(
#         user=request.user if request.user.is_authenticated else None,
#         session_key=request.session.session_key if not request.user.is_authenticated else None
#     )
#     total_price = cart_items.total_price(user=request.user)
#     total_quantity = cart_items.total_quantity()

#     return render(request, 'cart/cart.html', {
#         'items': cart_items,
#         'total_price': total_price,
#         'total_quantity': total_quantity
#     })

# def remove_from_cart(request, cart_id):
#     cart = get_object_or_404(Cart, id=cart_id)
#     cart.delete()
#     messages.success(request, 'Товар видалено з кошика.')
#     return redirect('cart_view')

# @login_required
# def checkout_view(request):
#     cart_items = Cart.objects.filter(user=request.user)
#     if not cart_items.exists():
#         messages.error(request, 'Ваш кошик порожній.')
#         return redirect('cart_view')

#     profile = request.user.profile
#     if not profile.phone or not profile.address:
#         messages.error(request, 'Заповніть профіль (телефон і адресу).')
#         return redirect('profile')

#     if request.method == 'POST':
#         order_data = {
#             'user': request.user,
#             'payment_method': request.POST.get('payment_method', 'cash'),
#             'delivery_method': request.POST.get('delivery_method', 'pickup'),
#             'recipient_name': request.POST.get('recipient_name', profile.user.get_full_name()),
#             'recipient_phone': request.POST.get('recipient_phone', profile.phone),
#             'address': profile.address,
#             'coupon': request.POST.get('coupon'),
#             'call_me': request.POST.get('call_me', False) == 'on',
#         }

#         if not order_data['recipient_name'] or not order_data['recipient_phone'] or not order_data['address']:
#             messages.error(request, 'Ім’я, телефон і адреса отримувача обов’язкові.')
#             return redirect('checkout')

#         with transaction.atomic():
#             order = Order.objects.create(**order_data)
#             total_discount = Decimal('0.00')
#             items_data = []

#             for cart_item in cart_items:
#                 subproduct = cart_item.product
#                 if not SubProducts.objects.filter(id=subproduct.id).exists():
#                     messages.error(request, f'Товар {subproduct} більше не доступний.')
#                     continue

#                 item_price = get_discounted_price(request.user, subproduct)['new_price']
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
#                 messages.error(request, 'Жоден товар у кошику не доступний.')
#                 return redirect('cart_view')

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

#         messages.success(request, 'Замовлення оформлено!')
#         return redirect('order_confirmation', order_id=order.id)

#     return render(request, 'cart/checkout.html', {
#         'cart_items': cart_items,
#         'profile': profile
#     })

# def order_confirmation(request, order_id):
#     order = get_object_or_404(Order, id=order_id, user=request.user)
#     return render(request, 'cart/order_confirmation.html', {'order': order})

# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from .models import Cart
# from order.models import Order, OrderItem
# from .serializers import CartSerializer
# from rest_framework import viewsets
# from rest_framework.response import Response
# from rest_framework.decorators import action
# from rest_framework.permissions import IsAuthenticatedOrReadOnly
# from product.models import SubProducts
# from product.utils import get_discounted_price
# from decimal import Decimal
# class CartViewSet(viewsets.ModelViewSet):
#     queryset = Cart.objects.all()
#     serializer_class = CartSerializer
#     permission_classes = [IsAuthenticatedOrReadOnly]

#     def get_queryset(self):
#         user = self.request.user
#         if user.is_authenticated:
#             return Cart.objects.filter(user=user)
#         session_key = self.request.session.session_key
#         if not session_key:
#             self.request.session.create()
#             session_key = self.request.session.session_key
#         return Cart.objects.filter(session_key=session_key)

#     def list(self, request, *args, **kwargs):
#         """Отримання списку корзин + загальної суми"""
#         cart_items = self.get_queryset()
#         serializer = self.get_serializer(cart_items, many=True)
#         total_sum = cart_items.total_price(user=request.user)
#         total_quantity = cart_items.total_quantity()

#         return Response({
#             "carts": serializer.data,
#             "total_sum_carts": total_sum,
#             "total_quantity": total_quantity
#         })

#     @action(detail=False, methods=['post'])
#     def add(self, request):
#         """Додавання товару до корзини"""
#         subproduct_id = request.data.get('subproduct_id')
#         quantity = int(request.data.get('quantity', 1))
#         subproduct = get_object_or_404(SubProducts, id=subproduct_id)

#         session_key = request.session.session_key
#         if not session_key:
#             request.session.create()
#             session_key = request.session.session_key

#         cart, created = Cart.objects.get_or_create(
#             user=request.user if request.user.is_authenticated else None,
#             session_key=session_key if not request.user.is_authenticated else None,
#             product=subproduct,
#             defaults={'quantity': quantity}
#         )
#         if not created:
#             cart.quantity += quantity
#             cart.save()

#         serializer = self.get_serializer(cart)
#         return Response(serializer.data)

#     @action(detail=True, methods=['delete'])
#     def remove(self, request, pk=None):
#         """Видалення товару з корзини"""
#         cart = get_object_or_404(Cart, pk=pk)
#         cart.delete()
#         return Response({"message": "Товар видалено з корзини"})
# def add_to_cart(request, subproduct_id):
#     subproduct = get_object_or_404(SubProducts, id=subproduct_id)
#     session_key = request.session.session_key
#     if not session_key:
#         request.session.create()
#         session_key = request.session.session_key

#     cart, created = Cart.objects.get_or_create(
#         user=request.user if request.user.is_authenticated else None,
#         session_key=session_key if not request.user.is_authenticated else None,
#         product=subproduct,
#         defaults={'quantity': 1}
#     )
#     if not created:
#         cart.quantity += 1
#         cart.save()

#     messages.success(request, f"{subproduct} додано до кошика.")
#     return redirect('cart_view')

# def cart_view(request):
#     cart_items = Cart.objects.filter(
#         user=request.user if request.user.is_authenticated else None,
#         session_key=request.session.session_key if not request.user.is_authenticated else None
#     )
#     total_price = cart_items.total_price(user=request.user)
#     total_quantity = cart_items.total_quantity()

#     return render(request, 'cart/cart.html', {
#         'items': cart_items,
#         'total_price': total_price,
#         'total_quantity': total_quantity
#     })

# def remove_from_cart(request, cart_id):
#     cart = get_object_or_404(Cart, id=cart_id)
#     cart.delete()
#     messages.success(request, 'Товар видалено з кошика.')
#     return redirect('cart_view')

# @login_required
# def checkout_view(request):
#     cart_items = Cart.objects.filter(user=request.user)
#     if not cart_items.exists():
#         messages.error(request, 'Ваш кошик порожній.')
#         return redirect('cart_view')

#     profile = request.user.profile
#     if not profile.phone or not profile.address:
#         messages.error(request, 'Заповніть профіль (телефон і адресу).')
#         return redirect('profile')

#     if request.method == 'POST':
#         order_data = {
#             'user': request.user,
#             'payment_method': request.POST.get('payment_method', 'cash'),
#             'delivery_method': request.POST.get('delivery_method', 'pickup'),
#             'recipient_name': request.POST.get('recipient_name', profile.user.get_full_name()),
#             'recipient_phone': request.POST.get('recipient_phone', profile.phone),
#             'address': profile.address,
#             'coupon': request.POST.get('coupon'),
#             'call_me': request.POST.get('call_me', False) == 'on',
#         }

#         if not order_data['recipient_name'] or not order_data['recipient_phone'] or not order_data['address']:
#             messages.error(request, 'Ім’я, телефон і адреса отримувача обов’язкові.')
#             return redirect('checkout')

#         with transaction.atomic():
#             order = Order.objects.create(**order_data)
#             total_discount = Decimal('0.00')
#             items_data = []

#             for cart_item in cart_items:
#                 subproduct = cart_item.product
#                 item_price = get_discounted_price(request.user, subproduct)['new_price']
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

#             OrderItem.objects.bulk_create(items_data)
#             order.calculate_total()
#             cart_items.delete()

#         messages.success(request, 'Замовлення оформлено!')
#         return redirect('order_confirmation', order_id=order.id)

#     return render(request, 'cart/checkout.html', {
#         'cart_items': cart_items,
#         'profile': profile
#     })

# def order_confirmation(request, order_id):
#     order = get_object_or_404(Order, id=order_id, user=request.user)
#     return render(request, 'cart/order_confirmation.html', {'order': order})

# from rest_framework.response import Response
# from rest_framework import viewsets
# from rest_framework.decorators import action
# from rest_framework.permissions import IsAuthenticatedOrReadOnly
# from .models import Cart
# from .serializers import CartSerializer
# from django.shortcuts import get_object_or_404
# from product.models import SubProducts


# # from rest_framework.response import Response
# # from rest_framework import viewsets
# # from .models import Cart
# # from .serializers import CartSerializer
# # from rest_framework.response import Response
# # from rest_framework import viewsets
# # from .models import Cart
# # from .serializers import CartSerializer

# # class CartViewSet(viewsets.ModelViewSet):
# #     queryset = Cart.objects.all()
# #     serializer_class = CartSerializer

# #     def list(self, request, *args, **kwargs):
# #         """Отримання списку корзин + загальної суми"""
# #         user = request.user

# #         # Визначаємо корзини користувача
# #         if user.is_authenticated:
# #             cart_items = Cart.objects.filter(user=user)
# #         else:
# #             session_key = request.session.session_key
# #             cart_items = Cart.objects.filter(session_key=session_key)

# #         # Серіалізуємо корзини
# #         serializer = self.get_serializer(cart_items, many=True)

# #         # Обчислюємо загальну суму всіх товарів у корзині
# #         total_sum = sum(item.products_price() for item in cart_items)

# #         # Формуємо відповідь без дублювання total_sum_carts
# #         return Response({
# #             "carts": serializer.data,  # список корзин
# #             "total_sum_carts": total_sum  # загальна сума всіх корзин
# #         })
