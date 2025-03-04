import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
import random
import string
from datetime import timedelta

User = get_user_model()

def generate_promo_code(length=10):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

class PromoCode(models.Model):
    code = models.CharField(max_length=20, unique=True, default=generate_promo_code, verbose_name=_("Промокод"))
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, verbose_name=_("Знижка, %"))
    valid_from = models.DateTimeField(verbose_name=_("Початок дії"))
    valid_to = models.DateTimeField(verbose_name=_("Кінець дії"))
    is_active = models.BooleanField(default=True, verbose_name=_("Активний"))
    usage_limit = models.PositiveIntegerField(default=1, verbose_name=_("Ліміт використання"))
    used_count = models.PositiveIntegerField(default=0, verbose_name=_("Використано"))
    applicable_products = models.ManyToManyField('product.Product', blank=True, related_name="promo_codes", verbose_name=_("Застосовується до товарів"))
    applicable_categories = models.ManyToManyField('product.Categories', blank=True, related_name="promo_codes", verbose_name=_("Застосовується до категорій"))
    created_at = models.DateTimeField(auto_now_add=True)
    
    def is_valid(self):
        return self.is_active and self.valid_from <= now() <= self.valid_to and self.used_count < self.usage_limit
    
    def use(self):
        if self.is_valid():
            self.used_count += 1
            self.save()
            return True
        return False

    def extend_validity(self, days):
        self.valid_to += timedelta(days=days)
        self.save()

    def __str__(self):
        return self.code


class Coupon(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="coupons", verbose_name=_("Користувач"))
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, verbose_name=_("Знижка, %"))
    valid_from = models.DateTimeField(verbose_name=_("Початок дії"))
    valid_to = models.DateTimeField(verbose_name=_("Кінець дії"))
    is_active = models.BooleanField(default=True, verbose_name=_("Активний"))
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return self.is_active and self.valid_from <= now() <= self.valid_to

    def extend_validity(self, days):
        self.valid_to += timedelta(days=days)
        self.save()

    def __str__(self):
        return f"Купон {self.discount_percentage}% для {self.user.email}"
class PriceHistory(models.Model):
    product = models.ForeignKey('product.Product', on_delete=models.CASCADE, related_name="price_history", verbose_name=_("Товар"))
    old_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Стара ціна"))
    new_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Нова ціна"))
    discount_applied = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Застосована знижка"))
    changed_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата зміни"))
    
    def __str__(self):
        return f"{self.product.name} | {self.old_price} -> {self.new_price}"


# class PriceHistory(models.Model):
#     product = models.ForeignKey('product.Product', on_delete=models.CASCADE, related_name="price_history", verbose_name=_("Товар"))
#     old_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Стара ціна"))
#     new_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Нова ціна"))
#     discount_applied = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Застосована знижка"))
#     changed_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата зміни"))
    
#     def __str__(self):
#         return f"{self.product} | {self.old_price} -> {self.new_price}"


class BirthdayDiscount(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="birthday_discount", verbose_name=_("Користувач"))
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=10, verbose_name=_("Знижка на день народження, %"))
    valid_days = models.PositiveIntegerField(default=7, verbose_name=_("Дійсна кількість днів"))
    created_at = models.DateTimeField(auto_now_add=True)
    
    def is_valid(self):
        if self.user.date_of_birth:
            start_date = self.user.date_of_birth.replace(year=now().year)
            end_date = start_date + timedelta(days=self.valid_days)
            return start_date <= now().date() <= end_date
        return False

    def __str__(self):
        return f"Знижка {self.discount_percentage}% для {self.user.email} на день народження"

# class PersonalDiscount(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="personal_discounts", verbose_name=_("Користувач"))
#     assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="assigned_discounts", verbose_name=_("Призначив"))
#     discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, verbose_name=_("Персональна знижка, %"))
#     valid_from = models.DateTimeField(verbose_name=_("Початок дії"))
#     valid_to = models.DateTimeField(verbose_name=_("Кінець дії"))
#     is_active = models.BooleanField(default=True, verbose_name=_("Активний"))
#     created_at = models.DateTimeField(auto_now_add=True)
#     user_groups = models.ManyToManyField('auth.Group', blank=True, related_name="group_discounts", verbose_name=_("Групи користувачів"))

#     def is_valid(self):
#         return self.is_active and self.valid_from <= now() <= self.valid_to

#     def __str__(self):
#         return f"{self.discount_percentage}% персональна знижка для {self.user.email}"

class PersonalDiscount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="personal_discounts", verbose_name=_("Користувач"))
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="assigned_discounts", verbose_name=_("Призначив"))
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, verbose_name=_("Персональна знижка, %"))
    valid_from = models.DateTimeField(verbose_name=_("Початок дії"))
    valid_to = models.DateTimeField(verbose_name=_("Кінець дії"))
    is_active = models.BooleanField(default=True, verbose_name=_("Активний"))
    applicable_products = models.ManyToManyField('product.Product', blank=True, related_name="personal_discounts", verbose_name=_("Застосовується до товарів"))
    applicable_categories = models.ManyToManyField('product.Categories', blank=True, related_name="personal_discounts", verbose_name=_("Застосовується до категорій"))
    user_groups = models.ManyToManyField('auth.Group', blank=True, related_name="group_discounts", verbose_name=_("Групи користувачів"))
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return self.is_active and self.valid_from <= now() <= self.valid_to

    def extend_validity(self, days):
        self.valid_to += timedelta(days=days)
        self.save()

    def __str__(self):
        return f"{self.discount_percentage}% персональна знижка для {self.user.email}"
class ProductDiscount(models.Model):
    product = models.ForeignKey('product.Product', on_delete=models.CASCADE, related_name="discounts", verbose_name=_("Товар"))
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, verbose_name=_("Знижка, %"))
    valid_from = models.DateTimeField(verbose_name=_("Початок дії"))
    valid_to = models.DateTimeField(verbose_name=_("Кінець дії"))
    is_active = models.BooleanField(default=True, verbose_name=_("Активний"))

    def is_valid(self):
        return self.is_active and self.valid_from <= now() <= self.valid_to

    def __str__(self):
        return f"{self.product.name} | {self.discount_percentage}%"
