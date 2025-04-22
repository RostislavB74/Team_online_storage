from django.db import models
from django.contrib.auth.models import User
from product.models import SubProducts
from decimal import Decimal

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    payment_method = models.CharField(
        max_length=20,
        choices=[('cash', 'Cash'), ('liqpay', 'LiqPay'), ('googlepay', 'GooglePay')],
        default='cash'
    )
    delivery_method = models.CharField(
        max_length=20,
        choices=[('pickup', 'Pickup'), ('delivery', 'Delivery')],
        default='pickup'
    )
    recipient_name = models.CharField(max_length=100, blank=True, null=True)
    recipient_phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    coupon = models.CharField(max_length=50, blank=True, null=True)
    call_me = models.BooleanField(default=False)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    final_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(
        max_length=20,
        choices=[('new', 'New'), ('paid', 'Paid'), ('failed', 'Failed'), ('reversed', 'Reversed')],
        default='new'
    )
    status_pay = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    def calculate_total(self):
        """Обчислює total_price і final_price з урахуванням знижок"""
        items = self.items.all()
        total_price = sum(item.total_price for item in items)
        discount = self.discount or Decimal('0.00')
        final_price = total_price * (1 - discount / 100)
        
        self.total_price = total_price
        self.final_price = round(final_price, 2)
        self.save()

    def __str__(self):
        return f'Order #{self.id} by {self.user or "Anonymous"}'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(SubProducts, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    product_price = models.DecimalField(max_digits=12, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'

    def save(self, *args, **kwargs):
        self.total_price = self.product_price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.product} x {self.quantity} in Order #{self.order.id}'

