from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class User(AbstractUser):
    phone = models.CharField(max_length=15, blank=True, null=True)

    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_set",  # Змінений related_name
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_permissions",  # Змінений related_name
        blank=True
    )

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.username