import uuid
from io import BytesIO

import qrcode
from django.core.cache import cache
from django.core.files.base import ContentFile
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver

from product.models import (
    Product,
    ProductAttributes,
    Categories,
    SubCategories,
    Material,
    SubProducts,
)
from project_1444.settings import CACHE_HEADERS_ENABLED


@receiver(post_save, sender=Product)
def create_subproduct_attributes(sender, instance, created, **kwargs):
    """Автоматично створює атрибути (ProductAttributes) для підпродукту"""
    if created and not ProductAttributes.objects.filter(product=instance).exists():
        ProductAttributes.objects.create(product=instance)


def clear_category_tree_cache():
    # Clear all cached variations
    if not CACHE_HEADERS_ENABLED:
        return
    pattern = "category_tree_*"
    print("Using clear_category_tree_cache ", pattern)
    try:
        if hasattr(cache, "delete_pattern"):
            # django-redis provides a delete_pattern method
            cache.delete_pattern(pattern)
        else:
            print("Clearing cache fully since django-redis is not used")
            cache.clear()
    except Exception as e:
        print(f"Error clearing cache: {e}")


@receiver(post_save, sender=Categories)
@receiver(post_delete, sender=Categories)
def category_changed(sender, instance, **kwargs):
    clear_category_tree_cache()


@receiver(post_save, sender=SubCategories)
@receiver(post_delete, sender=SubCategories)
def subcategory_changed(sender, instance, **kwargs):
    clear_category_tree_cache()


# Функція для генерації артикула перед збереженням
@receiver(pre_save, sender=Material)
def generate_material_article(sender, instance, **kwargs):
    if not instance.article:
        metal_code = (
            instance.material[0].upper() if instance.material else ""
        )  # Перевірка, чи є metal
        color_code = (
            instance.color[0].upper() if instance.color else ""
        )  # Перевірка, чи є color
        assay_code = (
            str(instance.assay) if instance.assay else ""
        )  # Перевірка, чи є assay
        last_material = sender.objects.order_by("-id").first()
        next_number = (
            f"{(last_material.id + 1) if last_material else 1:03d}"  # Генерація номера
        )
        instance.article = f"{metal_code}{assay_code}{color_code}{next_number}"


# Сигнал `pre_save` для автоматичного заповнення SKU, артикулу та QR-коду
@receiver(pre_save, sender=Product)
def product_pre_save(sender, instance, **kwargs):
    if not instance.sku:
        instance.sku = generate_sku()
    if not instance.article:
        instance.article = generate_product_new_article(instance)


@receiver(pre_save, sender=SubProducts)
def subproduct_pre_save(sender, instance, **kwargs):
    if not instance.sku:
        instance.sku = generate_sku()
    if not instance.article:
        instance.article = generate_subproduct_new_article(instance)
    if not instance.qr_code:
        instance.qr_code = generate_product_qr_code(instance)


def generate_sku():
    return f"SKU-{uuid.uuid4().hex[:8].upper()}"


def generate_product_qr_code(product):
    """Генерує QR-код із `sku` або `ean_13`"""
    qr_data = product.sku or product.ean_13 or product.name
    qr = qrcode.make(qr_data)
    qr_io = BytesIO()
    qr.save(qr_io, format="PNG")
    qr_file = ContentFile(qr_io.getvalue(), name=f"qr_{product.sku}.png")
    return qr_file


def generate_subproduct_new_article(instance):
    ModelClass: object = instance.__class__  # noqa N806
    last_product = ModelClass.objects.order_by("-id").first()
    # last_product = SubProducts.objects.order_by("-id").first()
    if last_product:
        # Припустимо, що перші два символи - це префікс
        last_article_number = int("".join(filter(str.isdigit, last_product.article)))
        new_article = (
            f"SBPR{last_article_number + 1:05d}"  # Формат: PR00001, PR00002, ...
        )
    else:
        new_article = "SBPR00001"  # Початковий SKU
    return new_article


def generate_product_new_article(instance):
    # def generate_sku():
    ModelClass: object = instance.__class__  # noqa N806
    last_product = ModelClass.objects.order_by("-id").first()
    # last_product = Product.objects.order_by("-id").first()
    if last_product:
        last_article_number = int("".join(filter(str.isdigit, last_product.article)))
        new_article = (
            f"PR{last_article_number + 1:05d}"  # Формат: PR00001, PR00002, ...
        )
    else:
        new_article = "PR00001"  # Початковий SKU
    return new_article
