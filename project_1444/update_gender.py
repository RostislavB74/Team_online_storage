# -*- coding: utf-8 -*-
import os
import sys
import django
from django.db import transaction
from .product.models import ProductAttributes, Gender

# from django.utils.translation import activate

# Додаємо корінь проєкту до sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)

# Налаштування Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project_1444.settings")
django.setup()

# Імпорт із правильного модуля


gender_map = {"male": "Чоловіче", "female": "Жіноче", "unisex": "Унісекс", "children": "Дитяче"}

with transaction.atomic():
    # Створюємо записи Gender і виводимо їх ID
    for gender_value in gender_map:
        gender, created = Gender.objects.get_or_create(gender=gender_value)
        if created:
            print(f"Created Gender: {gender_value} with ID {gender.id}")
        else:
            print(f"Gender {gender_value} already exists with ID {gender.id}")

    # Перевіряємо всі записи в product_gender
    print("Current Gender records:")
    for gender in Gender.objects.all():
        print(f"ID: {gender.id}, Gender: {gender.gender}")

    # Оновлюємо ProductAttributes
    for attr in ProductAttributes.objects.all():
        old_gender = getattr(attr, "old_gender", None) or getattr(attr, "gender", None)
        if old_gender and old_gender in gender_map:
            try:
                gender_obj = Gender.objects.get(gender=old_gender)
                attr.gender = gender_obj  # Призначаємо об'єкт Gender
                attr.save()
                print(f"Updated ProductAttributes ID {attr.id} with gender_id {gender_obj.id}")
            except Gender.DoesNotExist:
                print(f"Gender {old_gender} not found for ProductAttributes ID {attr.id}")
            except Exception as e:
                print(f"Error updating ProductAttributes ID {attr.id}: {str(e)}")
        else:
            print(f"No valid gender for ProductAttributes ID {attr.id}")
