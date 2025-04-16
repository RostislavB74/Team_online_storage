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
from datetime import timezone

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
    original_price = subproduct.price
    discounts = []

    # 1. Знижка на день народження
    if user and user.is_authenticated and hasattr(user, 'profile') and user.profile.birth_date:
        today = timezone.now().date()
        birthday = user.profile.birth_date.replace(year=today.year)
        if abs((today - birthday).days) <= 7:  # +/- 7 днів
            discounts.append({
                "type": "birthday",
                "value": Decimal("20.00"),  # 20%
                "exclusive": True
            })

    # 2. Персональна знижка
    if user and user.is_authenticated and hasattr(user, 'profile') and user.profile.personal_discount:
        discounts.append({
            "type": "personal",
            "value": user.profile.personal_discount,
            "exclusive": True
        })

    # 3. Акційна знижка на сам товар
    if subproduct.discount_percentage:
        discounts.append({
            "type": "product_discount",
            "value": subproduct.discount_percentage,
            "exclusive": False
        })

    # Обрати знижку:
    exclusive = [d for d in discounts if d["exclusive"]]
    if exclusive:
        best = max(exclusive, key=lambda d: d["value"])
        final_discount = best["value"]
    else:
        # Підсумовуємо всі неексклюзивні
        final_discount = sum([d["value"] for d in discounts])

    # Рахуємо ціну
    discount_multiplier = (100 - final_discount) / 100
    new_price = original_price * Decimal(discount_multiplier)

    return {
        "new_price": round(new_price, 2),
        "old_price": original_price,
        "discount_applied": final_discount
    }
# def get_discounted_price(user, subproduct):
#     original_price = subproduct.price
#     discounts = []

#     # 1. Знижка на день народження
#     if user.profile and user.profile.birth_date:
#         today = timezone.now().date()
#         birthday = user.profile.birth_date.replace(year=today.year)
#         if abs((today - birthday).days) <= 7:  # +/- 7 днів
#             discounts.append({
#                 "type": "birthday",
#                 "value": Decimal("20.00"),  # 20%
#                 "exclusive": True
#             })

#     # 2. Персональна знижка
#     if user.profile and user.profile.personal_discount:
#         discounts.append({
#             "type": "personal",
#             "value": user.profile.personal_discount,
#             "exclusive": True
#         })

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
#         # Підсумовуємо всі неексклюзивні
#         final_discount = sum([d["value"] for d in discounts])

#     # Рахуємо ціну
#     discount_multiplier = (100 - final_discount) / 100
#     new_price = original_price * Decimal(discount_multiplier)

#     return {
#         "new_price": round(new_price, 2),
#         "old_price": original_price,
#         "discount_applied": final_discount
#     }
