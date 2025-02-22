from celery import shared_task
from django.utils.timezone import now
from .models import Cart
from datetime import timedelta

@shared_task
def clear_old_carts():
    """Видаляє кошики, які не оновлювалися більше 7 днів"""
    old_carts = Cart.objects.filter(updated_at__lt=now() - timedelta(days=7))
    count = old_carts.delete()
    return f"Deleted {count} old carts"
