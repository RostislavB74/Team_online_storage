# import uuid
# import qrcode
# from datetime import datetime
# from io import BytesIO
# from django.db import models
# from django.db.models.signals import pre_save
# from django.core.files.base import ContentFile
# from django.dispatch import receiver
# from users.models import User
# from django.core.validators import MinValueValidator, MaxValueValidator
# from django.conf import settings
# from parler.models import TranslatableModel, TranslatedFields
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify


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
