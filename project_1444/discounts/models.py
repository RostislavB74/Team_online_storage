import uuid
import random
import string
from datetime import timedelta
from decimal import Decimal
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from django.conf import settings
from product.models import *
from users.models import UserProfile
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from django.contrib.auth.models import User
from product.models import Product, Categories, SubProducts
from users.models import UserProfile
from datetime import timedelta


def default_valid_to():
    return now() + timedelta(days=30)


User = get_user_model()


def generate_promo_code(length=10):
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


def generate_unique_promo_code():
    while True:
        code = generate_promo_code()
        if not PromoCode.objects.filter(code=code).exists():
            return code


class BaseDiscount(models.Model):
    valid_from = models.DateTimeField(verbose_name=_("Початок дії"))
    valid_to = models.DateTimeField(verbose_name=_("Кінець дії"))
    is_active = models.BooleanField(default=True, verbose_name=_("Активний"))
    combine_with_others = models.BooleanField(default=True)

    class Meta:
        abstract = True

    @property
    def is_valid(self):
        now_ = now()
        return self.is_active and self.valid_from <= now_ <= self.valid_to


class Discount(models.Model):
    class DiscountType(models.TextChoices):
        SEASONAL = "seasonal", _("Сезонна")
        BIRTHDAY = "birthday", _("День народження")
        PERSONAL = "personal", _("Персональна")
        MANUAL = "manual", _("Ручна")
        PROMO = "promo", _("Промокод")
        CATEGORY = "category", _("По категоріях")
        PRODUCT = "product", _("На продукт")
        OCCASION = "occasion", _("З приводу")
        COUPON = "coupon", _("Купон")
        MATERIAL = "material", _("На матеріал")
        STATUS = "status", _("На статус")
        GEMSTONE = "gemstone", _("На камінь")
        SIZE = "size", _("На розмір")
        GENDER = "gender", _("На стать")
        COLLECTION = "collection", _("На колекцію")
        STYLE = "style", _("На стиль")

    name = models.CharField(max_length=255)
    discount_type = models.CharField(max_length=20, choices=DiscountType.choices)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    combine_with_others = models.BooleanField(default=True)
    priority = models.PositiveIntegerField(default=0)

    profile = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, null=True, blank=True
    )

    # user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    products = models.ManyToManyField(Product, blank=True)
    categories = models.ManyToManyField(Categories, blank=True)
    occasions = models.ManyToManyField(Occasion, blank=True)
    materials = models.ManyToManyField(Material, blank=True)
    gemstones = models.ManyToManyField(Gemstone, blank=True)
    sizes = models.ManyToManyField(RingSizeConversion, blank=True)
    genders = models.ManyToManyField(Gender, blank=True)
    collections = models.ManyToManyField(Collections, blank=True)
    styles = models.ManyToManyField(Styles, blank=True)

    class Meta:
        ordering = ["-priority", "name"]
        verbose_name = _("Знижка")
        verbose_name_plural = _("Знижки")

    def is_valid(self, user=None):
        now_ = now()
        if not self.is_active or not (self.valid_from <= now_ <= self.valid_to):
            return False

        if self.discount_type == self.DiscountType.BIRTHDAY and user:
            return hasattr(user, "profile") and user.profile.is_birthday_today()

        return True

    def __str__(self):
        return f"{self.name} ({self.discount_percent}%)"


class PromoCode(BaseDiscount):
    code = models.CharField(
        max_length=20,
        unique=True,
        default=generate_unique_promo_code,
        verbose_name=_("Промокод"),
    )
    discount_percentage = models.DecimalField(
        max_digits=4, decimal_places=2, verbose_name=_("Знижка, %")
    )
    usage_limit = models.PositiveIntegerField(
        default=1, verbose_name=_("Ліміт використання")
    )
    used_count = models.PositiveIntegerField(default=0, verbose_name=_("Використано"))
    applicable_products = models.ManyToManyField(
        Product,
        blank=True,
        related_name="promo_codes",
        verbose_name=_("Застосовується до товарів"),
    )
    applicable_categories = models.ManyToManyField(
        Categories,
        blank=True,
        related_name="promo_codes",
        verbose_name=_("Застосовується до категорій"),
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Промо код")
        verbose_name_plural = _("Промо коди")

    @property
    def is_valid(self):
        return (
            self.is_active
            and self.valid_from <= now() <= self.valid_to
            and self.used_count < self.usage_limit
        )

    def use(self):
        if self.is_valid:
            self.used_count += 1
            self.save()
            return True
        return False

    def extend_validity(self, days):
        self.valid_to += timedelta(days=days)
        self.save()

    def __str__(self):
        return self.code


class DiscountUsageHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    promo_code = models.ForeignKey(
        PromoCode, on_delete=models.SET_NULL, null=True, blank=True
    )
    discount = models.ForeignKey(
        Discount, on_delete=models.SET_NULL, null=True, blank=True
    )
    used_at = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True, blank=True
    )
    order_id = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        ordering = ["-used_at"]
        verbose_name = _("Історія використання знижки")
        verbose_name_plural = _("Історії використання знижок")

    def __str__(self):
        return _("Promo code {} used for {}").format(self.promo_code, self.user.email)


class Coupon(BaseDiscount):
    profile = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="coupons",
        verbose_name=_("Користувач"),
    )
    # user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="coupons", verbose_name=_("Користувач"))
    discount_percentage = models.DecimalField(
        max_digits=4, decimal_places=2, verbose_name=_("Знижка, %")
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:

        verbose_name = _("Купон")
        verbose_name_plural = _("Купони")

    @property
    def is_valid(self):
        return self.is_active and self.valid_from <= now() <= self.valid_to

    def extend_validity(self, days):
        self.valid_to += timedelta(days=days)
        self.save()

    @property
    def email(self):
        return self.profile.user.email

    def __str__(self):
        return _("Купон {}% для {}").format(self.discount_percentage, self.email)


class PriceHistory(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="price_history",
        verbose_name=_("Товар"),
    )
    old_price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name=_("Стара ціна")
    )
    new_price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name=_("Нова ціна")
    )
    discount_applied = models.CharField(
        max_length=255, blank=True, null=True, verbose_name=_("Застосована знижка")
    )
    changed_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата зміни"))

    def __str__(self):
        return f"{self.product.name} | {self.old_price} -> {self.new_price}"


class BonusAccount(models.Model):
    profile = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="bonus_account",
        verbose_name=_("Користувач"),
    )
    # user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="bonus_account")
    balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Баланс бонусів"),
    )

    def __str__(self):
        return _("{} - {} бонусів").format(self.profile.user.username, self.balance)


class PersonalDiscount(BaseDiscount):
    profile = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="personal_discounts",
        verbose_name=_("Користувач"),
    )
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="assigned_discounts",
        verbose_name=_("Призначив"),
    )
    discount_percentage = models.DecimalField(
        max_digits=4, decimal_places=2, verbose_name=_("Персональна знижка, %")
    )
    applicable_products = models.ManyToManyField(
        Product,
        blank=True,
        related_name="personal_discounts",
        verbose_name=_("Застосовується до товарів"),
    )
    applicable_subproducts = models.ManyToManyField(
        SubProducts,
        blank=True,
        related_name="personal_discounts",
        verbose_name=_("Застосовується до субпродуктів"),
    )
    applicable_categories = models.ManyToManyField(
        Categories,
        blank=True,
        related_name="personal_discounts",
        verbose_name=_("Застосовується до категорій"),
    )
    user_groups = models.ManyToManyField(
        "auth.Group",
        blank=True,
        related_name="group_discounts",
        verbose_name=_("Групи користувачів"),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, verbose_name=_("Активна"))
    valid_from = models.DateTimeField(default=now, verbose_name=_("Дійсна з"))
    valid_to = models.DateTimeField(
        default=default_valid_to, verbose_name=_("Дійсна до")
    )

    class Meta:
        verbose_name = _("Персональна знижка")
        verbose_name_plural = _("Персональні знижки")

    @property
    def is_valid(self):
        return self.is_active and self.valid_from <= now() <= self.valid_to

    def extend_validity(self, days):
        self.valid_to += timedelta(days=days)
        self.save()

    @property
    def email(self):
        return self.profile.user.email

    def __str__(self):
        return _("{}% персональна знижка для {}").format(
            self.discount_percentage, self.email
        )


class BirthdayDiscount(models.Model):
    profile = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="birthday_discounts",  # Змінюємо related_name на множину, якщо кілька знижок
        verbose_name=_("Користувач"),
    )
    discount_percentage = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=Decimal("10.00"),
        verbose_name=_("Знижка на день народження, %"),
    )
    valid_days = models.PositiveIntegerField(
        default=7, verbose_name=_("Дійсна кількість днів")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    used_year = models.PositiveIntegerField(
        null=True, blank=True, verbose_name=_("Рік використання знижки")
    )
    birthday_at_creation = models.DateField(
        null=True, blank=True, verbose_name=_("Дата народження на момент створення")
    )

    def save(self, *args, **kwargs):
        # Зберігаємо дату народження на момент створення, якщо вона ще не встановлена
        if not self.pk and self.profile.birthday:
            self.birthday_at_creation = self.profile.birthday
        super().save(*args, **kwargs)

    @property
    def is_valid(self):
        today = now().date()

        # Перевіряємо, чи знижка вже використана в цьому році
        if self.used_year and self.used_year == today.year:
            return False

        # Використовуємо збережену дату народження
        if not self.birthday_at_creation:
            return False

        # Формуємо період дії знижки
        birthday_this_year = self.birthday_at_creation.replace(year=today.year)
        start_date = birthday_this_year
        end_date = birthday_this_year + timedelta(days=self.valid_days)

        # Перевіряємо, чи сьогодні входить у період дії знижки
        return start_date <= today <= end_date

    @property
    def email(self):
        return self.profile.user.email

    def __str__(self):
        return _("Знижка {}% для {} на день народження").format(
            self.discount_percentage, self.email
        )

    class Meta:
        verbose_name = _("Знижка на день народження")
        verbose_name_plural = _("Знижки на день народження")


# class BirthdayDiscount(models.Model):
#     profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='birthday_discount', verbose_name=_("Користувач"))
#     # user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="birthday_discount", verbose_name=_("Користувач"))
#     discount_percentage = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('10.00'), verbose_name=_("Знижка на день народження, %"))
#     valid_days = models.PositiveIntegerField(default=7, verbose_name=_("Дійсна кількість днів"))
#     created_at = models.DateTimeField(auto_now_add=True)

#     @property
#     def is_valid(self):
#         if self.profile.birthday:
#             today = now().date()
#             birthday_this_year = self.profile.birthday.replace(year=today.year)
#             start_date = birthday_this_year
#             end_date = birthday_this_year + timedelta(days=self.valid_days)
#             return start_date <= today <= end_date
#         return False
#     @property
#     def email(self):
#         return self.profile.user.email
#     def __str__(self):
#         return f"Знижка {self.discount_percentage}% для {self.email} на день народження"


class AbstractDiscount(models.Model):
    discount_percentage = models.DecimalField(
        max_digits=4, decimal_places=2, verbose_name=_("Знижка, %")
    )
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True

    @property
    def is_valid(self):
        return self.is_active and self.valid_from <= now() <= self.valid_to


class ProductDiscount(AbstractDiscount):
    product = models.ForeignKey(
        "product.Product",
        on_delete=models.CASCADE,
        related_name="product_discounts",
        verbose_name=_("Товар"),
    )

    def __str__(self):
        return f"{self.product.name} | {self.discount_percentage}%"


class MaterialDiscount(AbstractDiscount):
    material = models.ForeignKey(
        "product.Material",
        on_delete=models.CASCADE,
        related_name="material_discounts",
        verbose_name=_("Матеріал"),
    )

    def __str__(self):
        return f"{self.material.material} | {self.discount_percentage}%"


class StatusDiscount(AbstractDiscount):
    status = models.ForeignKey(
        "product.ProductStatus",
        on_delete=models.CASCADE,
        related_name="status_discounts",
        verbose_name=_("Статус"),
    )

    def __str__(self):
        return f"{self.status.name} | {self.discount_percentage}%"


class GemstoneDiscount(AbstractDiscount):
    gemstone = models.ForeignKey(
        "product.Gemstone",
        on_delete=models.CASCADE,
        related_name="gemstone_discounts",
        verbose_name=_("Каміння"),
    )

    def __str__(self):
        return f"{self.gemstone.name} | {self.discount_percentage}%"


class CategoryDiscount(AbstractDiscount):
    category = models.ForeignKey(
        "product.Categories",
        on_delete=models.CASCADE,
        related_name="categories_discounts",
        verbose_name=_("Категорії"),
    )

    def __str__(self):
        return f"{self.category.name} | {self.discount_percentage}%"


class SubcategoryDiscount(AbstractDiscount):
    subcategory = models.ForeignKey(
        "product.Subproducts",
        on_delete=models.CASCADE,
        related_name="subcategories_discounts",
        verbose_name=_("Підкатегорії"),
    )

    def __str__(self):
        return f"{self.subcategory.name} | {self.discount_percentage}%"


class CollectionDiscount(AbstractDiscount):
    collection = models.ForeignKey(
        "product.Collections",
        on_delete=models.CASCADE,
        related_name="collections_discounts",
        verbose_name=_("Колекції"),
    )

    def __str__(self):
        return f"{self.collection.name} | {self.discount_percentage}%"


class StylesDiscount(AbstractDiscount):
    style = models.ForeignKey(
        "product.Styles",
        on_delete=models.CASCADE,
        related_name="styles_discounts",
        verbose_name=_("Стилі"),
    )

    def __str__(self):
        return f"{self.style.name} | {self.discount_percentage}%"


class OccasionsDiscount(AbstractDiscount):
    occasions = models.ForeignKey(
        "product.Occasion",
        on_delete=models.CASCADE,
        related_name="occasions_discounts",
        verbose_name=_("Привід"),
    )

    def __str__(self):
        return f"{self.occasions.name} | {self.discount_percentage}%"


class SeasonDiscount(AbstractDiscount):
    name = models.CharField(max_length=255)  # Наприклад, "Зимова акція"
    categories = models.ManyToManyField(Categories, blank=True)  # або products

    def __str__(self):
        return f"{self.name} - {self.discount_percentage}%"
