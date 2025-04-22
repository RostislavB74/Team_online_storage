from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile, UserNotificationSettings

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, created, **kwargs):
    if created:
        # Створюємо UserProfile і UserNotificationSettings для нового користувача
        UserProfile.objects.create(user=instance)
        UserNotificationSettings.objects.create(user=instance)
    else:
        # Оновлюємо профіль, якщо він існує
        try:
            profile = instance.profile
            profile.save()
        except UserProfile.DoesNotExist:
            UserProfile.objects.create(user=instance)
        # Оновлюємо налаштування сповіщень, якщо вони існують
        try:
            notifications = instance.notifications
            notifications.save()
        except UserNotificationSettings.DoesNotExist:
            UserNotificationSettings.objects.create(user=instance)
#