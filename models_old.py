from django.db import models
from django.conf import settings
from product.models import Product

from django.db import models
from django.contrib.auth import get_user_model
from product.models import Product

User = get_user_model()

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cart")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def clear(self):
        """Очищуємо корзину після оформлення замовлення"""
        self.items.all().delete()
        self.total_price = 0
        self.save()

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)  # Фіксуємо ціну
    item_total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Вартість одиниці * кількість

    def save(self, *args, **kwargs):
        if self.product_price is None:
            self.product_price = self.product.price  # Беремо ціну товару, якщо вона не задана

        self.item_total_price = self.product_price * self.quantity  # Обчислюємо загальну вартість для цього товару
        super().save(*args, **kwargs)

        self.cart.total_price = sum(item.item_total_price for item in self.cart.items.all())  # Обновляємо загальну вартість корзини
        self.cart.save()
# class CartItem(models.Model):
#     cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     quantity = models.PositiveIntegerField(default=1)
#     product_price = models.DecimalField(max_digits=10, decimal_places=2)  # Фіксуємо ціну
#     total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

#     def save(self, *args, **kwargs):
#         if self.product_price is None:
#             self.product_price = self.product.price  # Виправляємо, якщо ціна не встановлена

#         self.total_price = self.product_price * self.quantity
#         super().save(*args, **kwargs)
# class CartItem(models.Model):
#     cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     quantity = models.PositiveIntegerField(default=1)
#     product_price = models.DecimalField(max_digits=10, decimal_places=2)  # Фіксуємо ціну
#     total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

#     def save(self, *args, **kwargs):
#         self.total_price = self.product_price * self.quantity
#         super().save(*args, **kwargs)

# class Cart(models.Model):
#     user = models.OneToOneField(
#         settings.AUTH_USER_MODEL, 
#         on_delete=models.CASCADE,
#         related_name="cart"
#     )
#     created_at = models.DateTimeField(auto_now_add=True)

#     def total_price(self):
#         return sum(item.total_price() for item in self.items.all())

#     def __str__(self):
#         return f"Кошик користувача {self.user.username}"


# class CartItem(models.Model):
#     cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     quantity = models.PositiveIntegerField(default=1)
#     added_at = models.DateTimeField(auto_now_add=True)

#     def total_price(self):
#         return self.product.price * self.quantity

#     def __str__(self):
#         return f"{self.quantity} x {self.product.name} у кошику {self.cart.user.username}"

