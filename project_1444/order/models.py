from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from product.models import Product
from django.contrib.auth.models import User
from decimal import Decimal
from discounts.models import Discount


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    selected_discount = models.ForeignKey(Discount, null=True, blank=True, on_delete=models.SET_NULL)
    final_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="orders", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    payment_method = models.CharField(max_length=50, choices=[("cash", "Готівка"), ("liqpay", "LiqPay"), ("googlepay", "Google Pay")], default="cash")
    delivery_method = models.CharField(max_length=50, choices=[("pickup", "Самовивіз"), ("courier", "Кур'єр"), ("nova_poshta", "Нова Пошта")], default="pickup")
    recipient_name = models.CharField(max_length=255, blank=True, null=True)
    recipient_phone = models.CharField(max_length=20, blank=True, null=True)
    coupon = models.CharField(max_length=50, blank=True, null=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(max_length=20, choices=[("new", "Нове"), ("processing", "Обробка"), ("paid", "Оплачене"), ("shipped", "Відправлене")], default="new")
    call_me = models.BooleanField(default=False)

    def calculate_total(self):
        self.total_price = sum(item.total_price for item in self.items.all())

        # автоматична знижка за великі суми
        if self.total_price > Decimal('10000.00'):
            self.discount = self.total_price * Decimal('0.05')  # 5% знижка
        else:
            self.discount = Decimal('0.00')

        self.final_price = self.total_price - self.discount
        self.save()
    
    def __str__(self):
        return f"Замовлення №{self.id} від {self.created_at.date()}"
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    def save(self, *args, **kwargs):
        self.total_price = self.product_price * self.quantity
        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.product.name} x {self.quantity} (₴{self.total_price})"

