from django.db import models
from django.contrib.auth import get_user_model
from product.models import Product

User = get_user_model()

class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Очікує оплати"),
        ("paid", "Оплачено"),
        ("shipped", "Відправлено"),
        ("canceled", "Скасовано"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    items = models.ManyToManyField(Product, through="OrderItem")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Замовлення #{self.id} - {self.user.username} ({self.get_status_display()})"

    def calculate_total_price(self):
        total = sum(item.price * item.quantity for item in self.order_items.all())
        self.total_price = total
        self.save()

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} ({self.order.id})"

    def save(self, *args, **kwargs):
        if not self.price:
            self.price = self.product.price  # Припускаємо, що у Product є поле price
        super().save(*args, **kwargs)
        self.order.calculate_total_price()

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
