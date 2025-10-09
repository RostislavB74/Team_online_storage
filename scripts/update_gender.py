# -*- coding: utf-8 -*-
import os
import sys
import django
from django.db import transaction
from project_1444.product.models import ProductAttributes, Gender
# from django.utils.translation import activate

# Додаємо корінь проєкту до sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)

# Налаштування Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project_1444.settings")
django.setup()

# Імпорт із правильного модуля


gender_map = {"female": "Жіноче", "male": "Чоловіче", "children": "Дитяче", "unisex": "Унісекс"}

with transaction.atomic():
    # Створюємо записи Gender
    for gender_value in gender_map:
        Gender.objects.get_or_create(gender=gender_value)

    # Оновлюємо ProductAttributes
    for attr in ProductAttributes.objects.all():
        old_gender = getattr(attr, "old_gender", None) or getattr(attr, "gender", None)
        if old_gender and old_gender in gender_map:
            try:
                gender_obj = Gender.objects.get(gender=old_gender)
                attr.gender = gender_obj
                attr.save()
                print(f"Updated ProductAttributes ID {attr.id} with gender {old_gender}")
            except Gender.DoesNotExist:
                print(f"Gender {old_gender} not found for ProductAttributes ID {attr.id}")
        else:
            print(f"No valid gender for ProductAttributes ID {attr.id}")
