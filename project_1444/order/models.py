from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from product.models import SubProducts
from discounts.models import Discount

class Order(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        related_name="orders", 
        null=True, 
        blank=True, 
        verbose_name='Користувач'
    )
    selected_discount = models.ForeignKey(
        Discount, 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL, 
        verbose_name='Обрана знижка'
    )
    final_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0, 
        verbose_name='Фінальна ціна'
    )
    total_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'), 
        verbose_name='Загальна ціна'
    )
    discount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'), 
        verbose_name='Знижка'
    )
    payment_method = models.CharField(
        max_length=50, 
        choices=[("cash", "Готівка"), ("liqpay", "LiqPay"), ("googlepay", "Google Pay")], 
        default="cash", 
        verbose_name='Спосіб оплати'
    )
    delivery_method = models.CharField(
        max_length=50, 
        choices=[("pickup", "Самовивіз"), ("courier", "Кур'єр"), ("nova_poshta", "Нова Пошта")], 
        default="pickup", 
        verbose_name='Спосіб доставки'
    )
    recipient_name = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        verbose_name='Ім’я отримувача'
    )
    recipient_phone = models.CharField(
        max_length=20, 
        blank=True, 
        null=True, 
        verbose_name='Телефон отримувача'
    )
    address = models.TextField(
        blank=True, 
        null=True, 
        verbose_name='Адреса доставки'
    )
    coupon = models.CharField(
        max_length=50, 
        blank=True, 
        null=True, 
        verbose_name='Купон'
    )
    status = models.CharField(
        max_length=20, 
        choices=[("new", "Нове"), ("processing", "Обробка"), ("paid", "Оплачене"), ("shipped", "Відправлене")], 
        default="new", 
        verbose_name='Статус'
    )
    call_me = models.BooleanField(
        default=False, 
        verbose_name='Передзвонити'
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name='Дата створення'
    )
    updated_at = models.DateTimeField(
        auto_now=True, 
        verbose_name='Дата оновлення'
    )

    class Meta:
        verbose_name = "Замовлення"
        verbose_name_plural = "Замовлення"

    def calculate_total(self):
        self.total_price = sum(item.total_price for item in self.items.all())
        if self.total_price > Decimal('10000.00'):
            self.discount = max(self.discount, self.total_price * Decimal('0.05'))
        self.final_price = self.total_price - self.discount
        self.save()

    def __str__(self):
        return f"Замовлення №{self.id} від {self.created_at.date()}"

class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name="items", 
        verbose_name='Замовлення'
    )
    product = models.ForeignKey(
        SubProducts, 
        on_delete=models.CASCADE, 
        verbose_name='Товар'
    )
    quantity = models.PositiveIntegerField(
        default=1, 
        verbose_name='Кількість'
    )
    product_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name='Ціна товару'
    )
    total_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name='Загальна ціна'
    )

    def save(self, *args, **kwargs):
        self.total_price = self.product_price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product} x {self.quantity} (₴{self.total_price})"

    class Meta:
        verbose_name = "Елемент замовлення"
        verbose_name_plural = "Елементи замовлення"
# from decimal import Decimal
# from django.db import models
# from django.contrib.auth.models import User
# from product.models import SubProducts  # Змінено на SubProducts
# from discounts.models import Discount
# from product.utils import get_discounted_price

# class Order(models.Model):
#     user = models.ForeignKey(
#         User, 
#         on_delete=models.SET_NULL, 
#         related_name="orders", 
#         null=True, 
#         blank=True, 
#         verbose_name='Користувач'
#     )
#     selected_discount = models.ForeignKey(
#         Discount, 
#         null=True, 
#         blank=True, 
#         on_delete=models.SET_NULL, 
#         verbose_name='Обрана знижка'
#     )
#     final_price = models.DecimalField(
#         max_digits=10, 
#         decimal_places=2, 
#         default=0, 
#         verbose_name='Фінальна ціна'
#     )
#     total_price = models.DecimalField(
#         max_digits=10, 
#         decimal_places=2, 
#         default=Decimal('0.00'), 
#         verbose_name='Загальна ціна'
#     )
#     discount = models.DecimalField(
#         max_digits=10, 
#         decimal_places=2, 
#         default=Decimal('0.00'), 
#         verbose_name='Знижка'
#     )
#     payment_method = models.CharField(
#         max_length=50, 
#         choices=[("cash", "Готівка"), ("liqpay", "LiqPay"), ("googlepay", "Google Pay")], 
#         default="cash", 
#         verbose_name='Спосіб оплати'
#     )
#     delivery_method = models.CharField(
#         max_length=50, 
#         choices=[("pickup", "Самовивіз"), ("courier", "Кур'єр"), ("nova_poshta", "Нова Пошта")], 
#         default="pickup", 
#         verbose_name='Спосіб доставки'
#     )
#     recipient_name = models.CharField(
#         max_length=255, 
#         blank=True, 
#         null=True, 
#         verbose_name='Ім’я отримувача'
#     )
#     recipient_phone = models.CharField(
#         max_length=20, 
#         blank=True, 
#         null=True, 
#         verbose_name='Телефон отримувача'
#     )
#     address = models.TextField(
#         blank=True, 
#         null=True, 
#         verbose_name='Адреса доставки'
#     )
#     coupon = models.CharField(
#         max_length=50, 
#         blank=True, 
#         null=True, 
#         verbose_name='Купон'
#     )
#     status = models.CharField(
#         max_length=20, 
#         choices=[("new", "Нове"), ("processing", "Обробка"), ("paid", "Оплачене"), ("shipped", "Відправлене")], 
#         default="new", 
#         verbose_name='Статус'
#     )
#     call_me = models.BooleanField(
#         default=False, 
#         verbose_name='Передзвонити'
#     )
#     created_at = models.DateTimeField(
#         auto_now_add=True, 
#         verbose_name='Дата створення'
#     )
#     updated_at = models.DateTimeField(
#         auto_now=True, 
#         verbose_name='Дата оновлення'
#     )

#     class Meta:
#         verbose_name = "Замовлення"
#         verbose_name_plural = "Замовлення"

#     def calculate_total(self):
#         self.total_price = sum(item.total_price for item in self.items.all())
#         # Знижка за великі суми
#         if self.total_price > Decimal('10000.00'):
#             self.discount = max(self.discount, self.total_price * Decimal('0.05'))
#         self.final_price = self.total_price - self.discount
#         self.save()

#     def __str__(self):
#         return f"Замовлення №{self.id} від {self.created_at.date()}"

# class OrderItem(models.Model):
#     order = models.ForeignKey(
#         Order, 
#         on_delete=models.CASCADE, 
#         related_name="items", 
#         verbose_name='Замовлення'
#     )
#     product = models.ForeignKey(
#         SubProducts,  # Змінено на SubProducts
#         on_delete=models.CASCADE, 
#         verbose_name='Товар'
#     )
#     quantity = models.PositiveIntegerField(
#         default=1, 
#         verbose_name='Кількість'
#     )
#     product_price = models.DecimalField(
#         max_digits=10, 
#         decimal_places=2, 
#         verbose_name='Ціна товару'
#     )
#     total_price = models.DecimalField(
#         max_digits=10, 
#         decimal_places=2, 
#         verbose_name='Загальна ціна'
#     )

#     def save(self, *args, **kwargs):
#         self.total_price = self.product_price * self.quantity
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return f"{self.product} x {self.quantity} (₴{self.total_price})"

#     class Meta:
#         verbose_name = "Елемент замовлення"
#         verbose_name_plural = "Елементи замовлення"


# from django.db import models
# from django.conf import settings
# from django.contrib.auth import get_user_model
# from product.models import Product
# from django.contrib.auth.models import User
# from decimal import Decimal
# from discounts.models import Discount

# # class Order(models.Model):
# #     user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
# #     profile = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True)
# #     total_price = models.DecimalField(max_digits=10, decimal_places=2)
# #     address = models.TextField()
# #     status = models.CharField(
# #         max_length=20,
# #         choices=[
# #             ("pending", _("Pending")),
# #             ("processing", _("Processing")),
# #             ("shipped", _("Shipped")),
# #             ("delivered", _("Delivered")),
# #         ],
# #         default="pending",
# #     )
# #     created_at = models.DateTimeField(auto_now_add=True)
# #     updated_at = models.DateTimeField(auto_now=True)

# #     def __str__(self):
# #         return f"Order {self.id} by {self.user}"

# # class OrderItem(models.Model):
# #     order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
# #     subproduct = models.ForeignKey(SubProducts, on_delete=models.SET_NULL, null=True)
# #     quantity = models.PositiveIntegerField()
# #     price = models.DecimalField(max_digits=10, decimal_places=2)  # Ціна на момент замовлення

# #     def __str__(self):
# #         return f"{self.quantity} x {self.subproduct}"
# class Order(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     selected_discount = models.ForeignKey(Discount, null=True, blank=True, on_delete=models.SET_NULL)
#     final_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="orders", null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     total_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
#     payment_method = models.CharField(max_length=50, choices=[("cash", "Готівка"), ("liqpay", "LiqPay"), ("googlepay", "Google Pay")], default="cash")
#     delivery_method = models.CharField(max_length=50, choices=[("pickup", "Самовивіз"), ("courier", "Кур'єр"), ("nova_poshta", "Нова Пошта")], default="pickup")
#     recipient_name = models.CharField(max_length=255, blank=True, null=True)
#     recipient_phone = models.CharField(max_length=20, blank=True, null=True)
#     coupon = models.CharField(max_length=50, blank=True, null=True)
#     discount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
#     status = models.CharField(max_length=20, choices=[("new", "Нове"), ("processing", "Обробка"), ("paid", "Оплачене"), ("shipped", "Відправлене")], default="new")
#     call_me = models.BooleanField(default=False)

#     def calculate_total(self):
#         self.total_price = sum(item.total_price for item in self.items.all())

#         # автоматична знижка за великі суми
#         if self.total_price > Decimal('10000.00'):
#             self.discount = self.total_price * Decimal('0.05')  # 5% знижка
#         else:
#             self.discount = Decimal('0.00')

#         self.final_price = self.total_price - self.discount
#         self.save()
    
#     def __str__(self):
#         return f"Замовлення №{self.id} від {self.created_at.date()}"
# class OrderItem(models.Model):
#     order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     quantity = models.PositiveIntegerField(default=1)
#     product_price = models.DecimalField(max_digits=10, decimal_places=2)
#     total_price = models.DecimalField(max_digits=10, decimal_places=2)
#     def save(self, *args, **kwargs):
#         self.total_price = self.product_price * self.quantity
#         super().save(*args, **kwargs)
#     def __str__(self):
#         return f"{self.product.name} x {self.quantity} (₴{self.total_price})"

