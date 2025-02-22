from django.db import models
from product.models import Product
from django.contrib.auth import get_user_model
from django.utils.timezone import now, timedelta
from rest_framework import serializers, viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

User = get_user_model()

class Warehouse(models.Model):
    name = models.CharField(max_length=255, unique=True)
    location = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class WarehouseStock(models.Model):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='stock')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='warehouses')
    quantity = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('warehouse', 'product')

    def __str__(self):
        return f"{self.product.name} - {self.warehouse.name}: {self.quantity}"

    def reserve_product(self, user, quantity, duration_minutes=30):
        if self.quantity < quantity:
            raise ValueError("Not enough stock available")
        
        expires_at = now() + timedelta(minutes=duration_minutes)
        reservation = Reservation.objects.create(
            user=user,
            product=self.product,
            warehouse=self.warehouse,
            quantity=quantity,
            expires_at=expires_at
        )
        self.quantity -= quantity
        self.save()
        return reservation

    def release_reservation(self, reservation):
        self.quantity += reservation.quantity
        reservation.delete()
        self.save()

class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reservations')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='reservations')
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        unique_together = ('product', 'warehouse', 'user')

    def __str__(self):
        return f"Reservation: {self.product.name} - {self.quantity} pcs at {self.warehouse.name}"

    def is_expired(self):
        return now() > self.expires_at

    def cancel_reservation(self):
        if self.is_expired():
            warehouse_stock = self.warehouse.stock.get(product=self.product)
            warehouse_stock.release_reservation(self)

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Order {self.id} - {self.status}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

# Serializers
class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = '__all__'

class WarehouseStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = WarehouseStock
        fields = '__all__'

class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'

# ViewSets
class WarehouseViewSet(viewsets.ModelViewSet):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    permission_classes = [permissions.IsAuthenticated]

class WarehouseStockViewSet(viewsets.ModelViewSet):
    queryset = WarehouseStock.objects.all()
    serializer_class = WarehouseStockSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def reserve(self, request, pk=None):
        stock = self.get_object()
        quantity = int(request.data.get('quantity', 0))
        if quantity <= 0:
            return Response({"error": "Invalid quantity"}, status=400)
        try:
            reservation = stock.reserve_product(request.user, quantity)
            return Response(ReservationSerializer(reservation).data)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)

class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        reservation = self.get_object()
        reservation.cancel_reservation()
        return Response({"message": "Reservation cancelled"})

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def create_order(self, request):
        user = request.user if request.user.is_authenticated else None
        reservations = Reservation.objects.filter(user=user)
        if not reservations.exists():
            return Response({"error": "No reserved products found"}, status=400)
        
        total_price = sum(res.quantity * res.product.price for res in reservations)
        order = Order.objects.create(user=user, total_price=total_price)
        
        for res in reservations:
            OrderItem.objects.create(
                order=order,
                product=res.product,
                quantity=res.quantity,
                price=res.product.price
            )
            res.delete()
        
        return Response(OrderSerializer(order).data)
# # @admin.register(Order)
# # class OrderAdmin(admin.ModelAdmin):
# #     list_display = ("id", "user", "total_price", "status", "updated_at")  # Перевір правильність імені
# #     list_filter = ("status", "created_at", "updated_at")
# #     search_fields = ("id", "user__name")
# @admin.register(OrderItem)
# class OrderItemAdmin(admin.ModelAdmin):
#     list_display = ('order', 'product', 'quantity', 'price')    
#     list_display_links = ('order', 'product')

# @admin.register(Order)
# class OrderAdmin(admin.ModelAdmin):
#     list_display = ('user', 'status', 'total_price', 'created_at', 'updated_at')
#     list_display_links = ('user', 'status')
# Admin Registration
admin.site.register(Warehouse)
admin.site.register(WarehouseStock)
admin.site.register(Reservation)
admin.site.register(Order)
admin.site.register(OrderItem)
# from rest_framework.routers import DefaultRouter
# from .views import OrderViewSet

# router = DefaultRouter()
# router.register(r'orders', OrderViewSet, basename='orders')

# urlpatterns = router.urls


# URL Routing
router = DefaultRouter()
router.register(r'warehouses', WarehouseViewSet)
router.register(r'warehouse-stock', WarehouseStockViewSet)
router.register(r'reservations', ReservationViewSet)
router.register(r'orders', OrderViewSet)

urlpatterns = [
    path('api/v1/', include(router.urls)),
]
# User = get_user_model()

# class Order(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
#     created_at = models.DateTimeField(auto_now_add=True)
#     status = models.CharField(max_length=50, default='pending')
#     products = models.ManyToManyField(Product, through='OrderItem')

# class OrderItem(models.Model):
#     order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     quantity = models.PositiveIntegerField()

# class Order(models.Model):
#     STATUS_CHOICES = [
#         ("pending", "Очікує оплати"),
#         ("paid", "Оплачено"),
#         ("shipped", "Відправлено"),
#         ("canceled", "Скасовано"),
#     ]

#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
#     items = models.ManyToManyField(Product, through="OrderItem")
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
#     total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"Замовлення #{self.id} - {self.user.username} ({self.get_status_display()})"

#     def calculate_total_price(self):
#         total = sum(item.price * item.quantity for item in self.order_items.all())
#         self.total_price = total
#         self.save()

# class OrderItem(models.Model):
#     order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_items")
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     quantity = models.PositiveIntegerField(default=1)
#     price = models.DecimalField(max_digits=10, decimal_places=2)

#     def __str__(self):
#         return f"{self.quantity} x {self.product.name} ({self.order.id})"

#     def save(self, *args, **kwargs):
#         if not self.price:
#             self.price = self.product.price  # Припускаємо, що у Product є поле price
#         super().save(*args, **kwargs)
#         self.order.calculate_total_price()
#     class Meta:
#         unique_together = ("order", "product")  
        
# from django.db import models
# from django.contrib.auth import get_user_model
# from product.models import Product

# User = get_user_model()

# class Order(models.Model):
#     STATUS_CHOICES = [
#         ("pending", "Очікує оплати"),
#         ("paid", "Оплачено"),
#         ("shipped", "Відправлено"),
#         ("canceled", "Скасовано"),
#     ]

#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
#     items = models.ManyToManyField(Product, through="OrderItem")
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
#     total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"Замовлення #{self.id} - {self.user.username} ({self.get_status_display()})"

# class OrderItem(models.Model):
#     order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_items")
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     quantity = models.PositiveIntegerField(default=1)
#     price = models.DecimalField(max_digits=10, decimal_places=2)

#     def __str__(self):
#         return f"{self.quantity} x {self.product.name} ({self.order.id})"


# window.APPLICATION = {
        # BITRIX_SESSID: '0dfe012d2ef9b3b372e51f9d7ced31e3',
        # SITE_DEFAULT_TEMPLATE_PATH : '/local/templates/.default',
        # SITE_TEMPLATE_PATH : '/local/templates/red_horse_order',
        # LANGUAGE_ID: 'ua',
        # PHONE_MASK: '\\+38 \\(0(5[0]{1}|6[3678]{1}|7[357]{1}|8[9]{1}|9[1-9]{1})\\) [0-9]{3}-[0-9]{2}-[0-9]{2}',
        # PHONE_MASK_FULL: '\\+38 \\(0(5[0]{1}|6[3678]{1}|7[357]{1}|8[9]{1}|9[1-9]{1})\\) [0-9]{3}-[0-9]{2}-[0-9]{2}',
        # USER_NAME: '',
        # USER_PHONE: '',
        # USER_EMAIL: '',
        # USER_ID: '0',
        # GTM_DISABLED: 'N',
        # RTB_HOUSE_DISABLED: 'N',
        # CATALOG_PATH: '/ua/yuvelirnye-ukrasheniya/',
        # IS_AUTHORIZE: Boolean(),
        # SHOW_HELP_CRUNCH: Boolean(1),
        # IS_MOBILE: Boolean(),
        #         USER: {
        #     ID: '0',
        #     FIRST_NAME: '',
        #     LAST_NAME: '',
        #     NAME: '',
        #     SURNAME:'',
        #     PHONE: '',
        #     EMAIL: ''
        # }
#  }