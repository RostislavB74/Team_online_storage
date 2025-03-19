from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Product, ProductAttributes, SubProducts

# @receiver(post_save, sender=Product)
# def create_product_subproducts(sender, instance, created, **kwargs):
#     """Автоматично створює підпродукт (SubProducts) при створенні Product"""
#     if created and not SubProducts.objects.filter(parent_product=instance).exists():
#         SubProducts.objects.create(parent_product=instance)

@receiver(post_save, sender=Product)
def create_subproduct_attributes(sender, instance, created, **kwargs):
    """Автоматично створює атрибути (ProductAttributes) для підпродукту"""
    if created and not ProductAttributes.objects.filter(product=instance).exists():
        ProductAttributes.objects.create(product=instance)
