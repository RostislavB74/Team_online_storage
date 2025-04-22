from django.db import models
from product.models import SubProducts
from django.contrib.auth.models import User
from product.utils import get_discounted_price

class CartQueryset(models.QuerySet):
    def total_price(self, user=None):
        return sum(cart.products_price(user) for cart in self)

    def total_quantity(self):
        if self:
            return sum(cart.quantity for cart in self)
        return 0

class Cart(models.Model):
    user = models.ForeignKey(
        to=User, 
        on_delete=models.CASCADE, 
        blank=True, 
        null=True, 
        verbose_name='Користувач'
    )
    product = models.ForeignKey(
        to=SubProducts, 
        on_delete=models.CASCADE, 
        verbose_name='Товар'
    )
    quantity = models.PositiveSmallIntegerField(
        default=0, 
        verbose_name='Кількість'
    )
    session_key = models.CharField(
        max_length=32, 
        null=True, 
        blank=True
    )
    created_timestamp = models.DateTimeField(
        auto_now_add=True, 
        verbose_name='Дата додавання'
    )

    class Meta:
        db_table = 'cart'
        verbose_name = "Корзина"
        verbose_name_plural = "Корзина"
        ordering = ("id",)
        unique_together = [['user', 'product'], ['session_key', 'product']]

    objects = CartQueryset().as_manager()

    def products_price(self, user=None):
        price = get_discounted_price(user, self.product)['new_price']
        return round(price * self.quantity, 2)

    def __str__(self):
        if self.user:
            return f'Корзина {self.user.username} | Товар {self.product} | Кількість {self.quantity}'
        return f'Анонімна корзина | Товар {self.product} | Кількість {self.quantity}'

