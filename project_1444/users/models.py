from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext as _
from datetime import timedelta
from django.utils import timezone

class MessengerDict:
    def __init__(self, data):
        self._data = data if isinstance(data, dict) else {}

    def __getattr__(self, key):
        return self._data.get(key, '')

    def __setattr__(self, key, value):
        if key == '_data':
            super().__setattr__(key, value)
        else:
            self._data[key] = value

    def __str__(self):
        return str(self._data)

    def to_dict(self):
        return self._data

def default_expires_at():
    return timezone.now() + timedelta(minutes=5)

class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="otps")
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=default_expires_at)

    def __str__(self):
        return f"OTP {self.code} for {self.user.username}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    gender = models.CharField(
        max_length=1,
        choices=[("M", _("Male")), ("F", _("Female"))],
        blank=True,
        null=True,
    )
    _messengers = models.JSONField(default=dict, blank=True, db_column='messengers')

    @property
    def messengers(self):
        return MessengerDict(self._messengers)

    @messengers.setter
    def messengers(self, value):
        if not isinstance(value, dict):
            raise ValueError("Messengers must be a dictionary")
        self._messengers = value

    def get_messengers_for_admin(self):
        return self._messengers  # Повертає сирий словник для адмінки

    phone = models.CharField(max_length=15, blank=True, null=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)
    partner_name = models.CharField(max_length=100, blank=True, null=True)
    partner_birthday = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    wedding_date = models.DateField(blank=True, null=True)
    occasions_personal = models.CharField(max_length=100, blank=True, null=True)
    occasions_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    class Child(models.Model):
        profile = models.ForeignKey(
            "UserProfile", on_delete=models.CASCADE, related_name="children"
        )
        name = models.CharField(max_length=100)
        birthday = models.DateField()

class UserAddress(models.Model):
    DELIVERY_TYPE_CHOICES = [
        ("home", "Звичайна адреса"),
        ("nova_poshta", "Нова Пошта"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    delivery_type = models.CharField(
        max_length=20, choices=DELIVERY_TYPE_CHOICES, default="home"
    )
    city = models.CharField(max_length=100)
    street = models.CharField(max_length=255, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    nova_poshta_branch = models.CharField(max_length=50, blank=True, null=True)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        if self.delivery_type == "nova_poshta":
            return f"Нова Пошта - {self.city}, Відділення {self.nova_poshta_branch}"
        return f"{self.city}, {self.street} ({self.user.username})"

class UserNotificationSettings(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="notifications"
    )
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    viber_notifications = models.BooleanField(default=False)

    def __str__(self):
        return f"Notifications for {self.user.username}"

