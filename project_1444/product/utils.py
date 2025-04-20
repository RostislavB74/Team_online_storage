import uuid
import qrcode
from datetime import datetime
from io import BytesIO
from django.db import models
from django.db.models.signals import pre_save
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from decimal import Decimal
from django.utils import timezone
from parler.utils.context import switch_language
from django.db.models import Q

def save_with_translation(instance, *args, **kwargs):
    """Зберігає об'єкт і створює переклад, якщо його немає."""
    is_new = instance.pk is None  # Перевіряємо, чи новий об'єкт
    super(instance.__class__, instance).save(*args, **kwargs)  # Зберігаємо об'єкт

    current_language = instance.get_current_language()
    instance.set_current_language(current_language)

    # Перевіряємо, чи існує переклад
    try:
        translation = instance.get_translation(current_language)
    except instance.translations.model.DoesNotExist:
        name = getattr(instance, "name", "translation")  # Переконуємося, що є ім'я
        slug = slugify(name)  # Генеруємо slug
        translation = instance.translations.create(
            language_code=current_language, name=name, slug=slug
        )
    if not translation.slug and translation.name:
        translation.slug = slugify(translation.name)
        translation.save()  # Зберігаємо переклад окремо
    return instance

def get_discounted_price(user, subproduct):
    """
    Обчислює ціну з урахуванням знижок.
    Повертає словник із:
    - new_price: Ціна після знижки (Decimal)
    - old_price: Оригінальна ціна (Decimal)
    - discount_applied: Застосований відсоток знижки (Decimal)
    """
    print(f"User: {user}, Subproduct: {subproduct}, Authenticated: {user.is_authenticated if user else False}")
    original_price = subproduct.price
    discounts = []

    # 1. Знижка на день народження
    if user and user.is_authenticated and hasattr(user, 'profile') and user.profile.birthday:
        print(f"Checking birthday for user: {user.username}, Birthday: {user.profile.birthday}")
        today = timezone.now().date()
        print(f"Today: {today}")
        birthday = user.profile.birthday.replace(year=today.year)
        if abs((today - birthday).days) <= 7:  # +/- 7 днів
            discounts.append({
                "type": "birthday",
                "value": Decimal("20.00"),  # 20% знижка
                "exclusive": True
            })

    # 2. Персональна знижка
    if user and user.is_authenticated and hasattr(user, 'profile'):
        today = timezone.now()
        personal_discounts_query = user.profile.personal_discounts.filter(
            is_active=True,
            valid_from__lte=today,
            valid_to__gte=today
        )

        if subproduct and hasattr(subproduct, 'parent_product') and subproduct.parent_product and subproduct.parent_product.category:
            personal_discounts = personal_discounts_query.filter(
                Q(applicable_products=subproduct.parent_product) |
                Q(applicable_subproducts=subproduct) |
                Q(applicable_categories=subproduct.parent_product.category) |
                Q(applicable_products__isnull=True, applicable_categories__isnull=True, applicable_subproducts__isnull=True)
            ).distinct()
        else:
            personal_discounts = personal_discounts_query.filter(
                applicable_products__isnull=True,
                applicable_categories__isnull=True,
                applicable_subproducts__isnull=True
            ).distinct()

        if personal_discounts.exists():
            max_discount = personal_discounts.order_by('-discount_percentage').first()
            print(f"Personal discount for user: {user.username}, Discount: {max_discount.discount_percentage}%")
            discounts.append({
                "type": "personal",
                "value": max_discount.discount_percentage,
                "exclusive": True
            })

    # 3. Акційна знижка на сам товар
    if subproduct.discount_percentage:
        discounts.append({
            "type": "product_discount",
            "value": subproduct.discount_percentage,
            "exclusive": False
        })

    # Обираємо знижку
    exclusive = [d for d in discounts if d["exclusive"]]
    if exclusive:
        best = max(exclusive, key=lambda d: d["value"])
        final_discount = best["value"]
    else:
        final_discount = sum([d["value"] for d in discounts])

    # Обчислюємо ціну
    discount_multiplier = (100 - final_discount) / 100
    new_price = original_price * Decimal(discount_multiplier)

    print(f"Original price: {original_price}, Discount applied: {final_discount}%, New price: {new_price}")
    return {
        "new_price": round(new_price, 2),
        "old_price": original_price,
        "discount_applied": final_discount
    }
# import uuid
# import qrcode
# from datetime import datetime
# from io import BytesIO
# from django.db import models
# from django.db.models.signals import pre_save
# from django.conf import settings
# from django.core.files.base import ContentFile
# from django.core.validators import MinValueValidator, MaxValueValidator
# from django.utils.translation import gettext_lazy as _
# from django.utils.text import slugify
# from decimal import Decimal
# from django.utils import timezone
# from parler.utils.context import switch_language
# from django.db.models import Q

# def save_with_translation(instance, *args, **kwargs):
#     """Зберігає об'єкт і створює переклад, якщо його немає."""
#     is_new = instance.pk is None  # Перевіряємо, чи новий об'єкт
#     super(instance.__class__, instance).save(*args, **kwargs)  # Зберігаємо об'єкт

#     current_language = instance.get_current_language()
#     instance.set_current_language(current_language)

#     # Перевіряємо, чи існує переклад
#     try:
#         translation = instance.get_translation(current_language)
#     except instance.translations.model.DoesNotExist:
#         name = getattr(instance, "name", "translation")  # Переконуємося, що є ім'я
#         slug = slugify(name)  # Генеруємо slug
#         translation = instance.translations.create(
#             language_code=current_language, name=name, slug=slug
#         )
#     if not translation.slug and translation.name:
#         translation.slug = slugify(translation.name)
#         translation.save()  # Зберігаємо переклад окремо
#     return instance
# def get_discounted_price(user, subproduct):
#     print(f"User: {user}, Subproduct: {subproduct}, Authenticated: {user.is_authenticated if user else False}")  # Дебаг
#     original_price = subproduct.price
#     discounts = []

#     # 1. Знижка на день народження
#     if user and user.is_authenticated and hasattr(user, 'profile') and user.profile.birthday:
#         print(f"Checking birthday for user: {user.username}, Birthday: {user.profile.birthday}")  # Дебаг
#         today = timezone.now().date()
#         print(f"Today: {today}")  # Дебаг
#         birthday = user.profile.birthday.replace(year=today.year)
#         if abs((today - birthday).days) <= 7:  # +/- 7 днів
#             discounts.append({
#                 "type": "birthday",
#                 "value": Decimal("20.00"),  # 20%
#                 "exclusive": True
#             })

#     # 2. Персональна знижка
#     if user and user.is_authenticated and hasattr(user, 'profile'):
#         today = timezone.now()
#         personal_discounts_query = user.profile.personal_discounts.filter(
#             is_active=True,
#             valid_from__lte=today,
#             valid_to__gte=today
#         )

#         if subproduct and hasattr(subproduct, 'parent_product') and subproduct.parent_product and subproduct.parent_product.category:
#             personal_discounts = personal_discounts_query.filter(
#                 Q(applicable_products=subproduct.parent_product) |
#                 Q(applicable_subproducts=subproduct) |
#                 Q(applicable_categories=subproduct.parent_product.category) |
#                 Q(applicable_products__isnull=True, applicable_categories__isnull=True, applicable_subproducts__isnull=True)
#             ).distinct()
#         else:
#             personal_discounts = personal_discounts_query.filter(
#                 applicable_products__isnull=True,
#                 applicable_categories__isnull=True,
#                 applicable_subproducts__isnull=True
#             ).distinct()

#         if personal_discounts.exists():
#             max_discount = personal_discounts.order_by('-discount_percentage').first()
#             print(f"Personal discount for user: {user.username}, Discount: {max_discount.discount_percentage}%")  # Дебаг
#             discounts.append({
#                 "type": "personal",
#                 "value": max_discount.discount_percentage,
#                 "exclusive": True
#             })

#     # 3. Акційна знижка на сам товар
#     if subproduct.discount_percentage:
#         discounts.append({
#             "type": "product_discount",
#             "value": subproduct.discount_percentage,
#             "exclusive": False
#         })

#     # Обрати знижку:
#     exclusive = [d for d in discounts if d["exclusive"]]
#     if exclusive:
#         best = max(exclusive, key=lambda d: d["value"])
#         final_discount = best["value"]
#     else:
#         final_discount = sum([d["value"] for d in discounts])

#     # Рахуємо ціну
#     discount_multiplier = (100 - final_discount) / 100
#     new_price = original_price * Decimal(discount_multiplier)

#     return {
#         "new_price": round(new_price, 2),
#         "old_price": original_price,
#         "discount_applied": final_discount
#     }
