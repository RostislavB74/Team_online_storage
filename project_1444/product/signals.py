from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django_redis import get_redis_connection

from .models import Product, ProductAttributes, SubProducts, Categories, SubCategories


@receiver(post_save, sender=Product)
def create_subproduct_attributes(sender, instance, created, **kwargs):
    """Автоматично створює атрибути (ProductAttributes) для підпродукту"""
    if created and not ProductAttributes.objects.filter(product=instance).exists():
        ProductAttributes.objects.create(product=instance)


def clear_category_tree_cache():
    # Clear all cached variations
    pattern = "category_tree_*"
    print("Using clear_category_tree_cache ", pattern)
    try:
        if hasattr(cache, "delete_pattern"):
            # django-redis provides a delete_pattern method
            cache.delete_pattern(pattern)
        else:
            raise NotImplementedError(f"Redis cache backend {cache.__class__.__name__}")
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
