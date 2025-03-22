from django.db import models
from product.models import SubProducts

from django.contrib.auth.models import User


class CartQueryset(models.QuerySet):
    
    def total_price(self):
        return sum(cart.products_price() for cart in self)
    
    def total_quantity(self):
        if self:
            return sum(cart.quantity for cart in self)
        return 0
    

class Cart(models.Model):

    user = models.ForeignKey(to=User, on_delete=models.CASCADE, blank=True, null=True, verbose_name='Користувач')
    product = models.ForeignKey(to=SubProducts, on_delete=models.CASCADE, verbose_name='Товар')
    quantity = models.PositiveSmallIntegerField(default=0, verbose_name='Кількість')
    session_key = models.CharField(max_length=32, null=True, blank=True)
    created_timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Дата додавання')

    class Meta:
        db_table = 'cart'
        verbose_name = "Корзина"
        verbose_name_plural = "Корзина"
        ordering = ("id",)

    objects = CartQueryset().as_manager()

    def products_price(self):
        return round(self.product.price * self.quantity, 2)


    def __str__(self):
        if self.user:
            return f'Корзина {self.user.username} | Товар {self.product} | Кількість {self.quantity}'
            
        return f'Анонімна корзина | Товар {self.product} | Кількість {self.quantity}'


# import uuid
# from uuid import uuid4
# from django.conf import settings
# from django.db import models
# from django.contrib.auth import get_user_model
# from django.utils.timezone import now

# User = get_user_model()

# class Cart(models.Model):
#     user = models.OneToOneField(
#         settings.AUTH_USER_MODEL, 
#         on_delete=models.CASCADE,
#         related_name="cart",
#         null=True,  # Для незареєстрованих користувачів це буде None
#         blank=True
#     )
#     uuid = models.UUIDField(default=uuid4, unique=True, db_index=True)  # Для анонімних користувачів
#     created_at = models.DateTimeField(auto_now_add=True)
#     last_updated = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"Cart {self.uuid} ({'User: ' + str(self.user.id) if self.user else 'Anonymous'})"

#     def merge_with(self, other_cart):
#         """Об'єднує два кошики (наприклад, після авторизації)."""
#         for item in other_cart.items.all():
#             existing_item = self.items.filter(product=item.product).first()
#             if existing_item:
#                 existing_item.quantity += item.quantity
#                 existing_item.save()
#             else:
#                 item.cart = self
#                 item.save()
#         other_cart.delete()

#     def update_timestamp(self):
#         """Оновлення часу останньої активності."""
#         self.last_updated = now()
#         self.save(update_fields=["updated_at"])
# class CartItem(models.Model):
#     cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
#     product = models.ForeignKey("product.Product", on_delete=models.CASCADE)
#     quantity = models.PositiveIntegerField(default=1)
#     # product_price = models.ForeignKey("price.Product",on_delete=models.CASCADE)

#     def __str__(self):
#         return f"{self.quantity} x {self.product.name} (Cart {self.cart.uuid})"



# # from django.db import models
# # from django.conf import settings
# # from product.models import Product

# # class Cart(models.Model):
# #     user = models.OneToOneField(
# #         settings.AUTH_USER_MODEL, 
# #         on_delete=models.CASCADE,
# #         related_name="cart"
# #     )
# #     created_at = models.DateTimeField(auto_now_add=True)

# #     def total_price(self):
# #         return sum(item.total_price() for item in self.items.all())

# #     def __str__(self):
# #         return f"Кошик користувача {self.user.username}"


# # class CartItem(models.Model):
# #     cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
# #     product = models.ForeignKey(Product, on_delete=models.CASCADE)
# #     quantity = models.PositiveIntegerField(default=1)
# #     added_at = models.DateTimeField(auto_now_add=True)

# #     def total_price(self):
# #         return self.product.price * self.quantity

# #     def __str__(self):
# #         return f"{self.quantity} x {self.product.name} у кошику {self.cart.user.username}"

# #     class Meta:
# #         unique_together = ("cart", "product")
# #         verbose_name = "Товар у кошику"
# #         verbose_name_plural = "Товари у кошику"
# from django.db import models
# from django.conf import settings
# from product.models import Product
# from django.contrib.auth import get_user_model
# # from users.models import User

# User = get_user_model()


# # class Cart(models.Model):
# #     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
# #     products = models.ManyToManyField(Product, through='CartItem')


# # class CartItem(models.Model):
# #     cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
# #     product = models.ForeignKey(Product, on_delete=models.CASCADE)
# #     quantity = models.PositiveIntegerField(default=1)



# class Cart(models.Model):
#     user = models.OneToOneField(
#         settings.AUTH_USER_MODEL, 
#         on_delete=models.CASCADE,
#         related_name="cart"
#     )
#     created_at = models.DateTimeField(auto_now_add=True)

#     @property
#     def total_price(self):
#         return sum(item.total_price for item in self.items.all())

#     def __str__(self):
#         return f"Кошик користувача {self.user.name}"


# class CartItem(models.Model):
#     cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     quantity = models.PositiveIntegerField(default=1)
#     added_at = models.DateTimeField(auto_now_add=True)

#     @property
#     def total_price(self):
#         return self.product.price * self.quantity

#     def __str__(self):
#         return f"{self.quantity} x {self.product.name} у кошику {self.cart.user.name}"

#     class Meta: 
#         unique_together = ("cart", "product")
#         verbose_name = "Товар у кошику"
#         verbose_name_plural = "Товари у кошику"