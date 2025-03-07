from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Product, ProductAttributes

@receiver(post_save, sender=Product)
def create_product_attributes(sender, instance, created, **kwargs):
    if created and not hasattr(instance, "attributes"):
        ProductAttributes.objects.create(product=instance)  # Не передаємо `name` та `slug`
        