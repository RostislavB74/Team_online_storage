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
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.contrib.auth.models import User
# from users.models import UserProfile
# import logging

# logger = logging.getLogger(__name__)

# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     try:
#         # Перевіряємо, чи існує профіль
#         if not hasattr(instance, 'profile'):
#             logger.info(f"Creating UserProfile for user {instance.username}")
#             UserProfile.objects.create(user=instance)
#         else:
#             logger.info(f"UserProfile already exists for user {instance.username}")
#     except Exception as e:
#         logger.error(f"Error creating UserProfile for user {instance.username}: {e}")
# # @receiver(post_save, sender=User)
# # def save_user_profile(sender, instance, **kwargs):
# #     try:
# #         if hasattr(instance, 'profile') and instance.profile._state.has_changed():
# #             instance.profile.save()
# #     except UserProfile.DoesNotExist:
# #         UserProfile.objects.create(user=instance)
# # from django.db.models.signals import post_save
# # from django.dispatch import receiver
# # from django.contrib.auth.models import User
# # from .models import UserProfile

# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.contrib.auth.models import User
# from .models import UserProfile, UserNotificationSettings

# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, created, **kwargs):
#     if created:
#         # Створюємо UserProfile і UserNotificationSettings для нового користувача
#         UserProfile.objects.create(user=instance)
#         UserNotificationSettings.objects.create(user=instance)
#     else:
#         # Оновлюємо профіль, якщо він існує
#         try:
#             profile = instance.profile
#             profile.save()
#         except UserProfile.DoesNotExist:
#             UserProfile.objects.create(user=instance)
#         # Оновлюємо налаштування сповіщень, якщо вони існують
#         try:
#             notifications = instance.notifications
#             notifications.save()
#         except UserNotificationSettings.DoesNotExist:
#             UserNotificationSettings.objects.create(user=instance)

# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         UserProfile.objects.create(user=instance)

# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     try:
#         # Перевіряємо, чи існує профіль і чи він змінений
#         if hasattr(instance, 'profile') and instance.profile._state.has_changed():
#             instance.profile.save()
#     except UserProfile.DoesNotExist:
#         # Якщо профіль не існує, створюємо його
#         UserProfile.objects.create(user=instance)
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.contrib.auth.models import User
# from users.models import UserProfile

# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         UserProfile.objects.create(user=instance)
# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     instance.profile.save()

