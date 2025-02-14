import phonenumbers
from ipware import get_client_ip
import random
from django.contrib.auth.models import Group
from django.db import transaction
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from rest_framework_simplejwt.tokens import RefreshToken


# User Manager
import phonenumbers
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group
from django.db import models
from ipware import get_client_ip

class UserManager(BaseUserManager):
    def get_country_from_ip(self, request):
        """Визначає країну за IP (якщо можливо)."""
        from django.contrib.gis.geoip2 import GeoIP2
        
        ip, is_routable = get_client_ip(request)
        if ip:
            try:
                geo = GeoIP2()
                country_code = geo.country(ip)["country_code"]
                return country_code
            except Exception:
                pass  # Якщо визначити не вдалося, повернемо None
        return None

    def normalize_phone(self, phone, country=None):
        """Перевіряє, нормалізує та повертає телефон у міжнародному форматі."""
        if not phone:
            return None

        if not country:
            country = "UA"  # Значення за замовчуванням

        try:
            parsed_number = phonenumbers.parse(phone, country)
            if not phonenumbers.is_valid_number(parsed_number):
                raise ValidationError("Invalid phone number")
            return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)  # +380XXXXXXXXX
        except phonenumbers.NumberParseException:
            raise ValidationError("Invalid phone number format")

    def create_user(self, name, email=None, phone=None, telegram=None, password=None, request=None, **extra_fields):
        if not name:
            raise ValueError("User must have a name")
        
        if not email and not phone and not telegram:
            raise ValueError("User must have at least one contact method (email, phone, or Telegram)")

        # Визначаємо країну за IP, якщо вона не передана вручну
        country = extra_fields.pop("country", None) or (self.get_country_from_ip(request) if request else "UA")

        email = self.normalize_email(email) if email else None
        phone = self.normalize_phone(phone, country)  # Нормалізуємо телефон

        user = self.model(name=name, email=email, phone=phone, telegram=telegram, **extra_fields)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)

        # Додаємо користувача до групи "Користувачі" за замовчуванням
        group, created = Group.objects.get_or_create(name="Користувачі")
        user.groups.add(group)

        return user

    def create_superuser(self, name, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(name=name, email=email, password=password, **extra_fields)

# class UserManager(BaseUserManager):
#     def normalize_phone(self, phone, country="UA"):
#         """Перевіряє, нормалізує та повертає телефон у міжнародному форматі."""
#         if not phone:
#             return None  

#         try:
#             parsed_number = phonenumbers.parse(phone, country)
#             if not phonenumbers.is_valid_number(parsed_number):
#                 raise ValidationError("Invalid phone number")
#             return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)  # +380XXXXXXXXX
#         except phonenumbers.NumberParseException:
#             raise ValidationError("Invalid phone number format")

#     def create_user(self, name, email=None, phone=None, telegram=None, password=None, **extra_fields):
#         if not name:
#             raise ValueError("User must have a name")

#         if not email and not phone and not telegram:
#             raise ValueError("User must have at least one contact method (email, phone, or Telegram)")

#         email = self.normalize_email(email) if email else None
#         phone = self.normalize_phone(phone) 

#         with transaction.atomic():  
#             user = self.model(name=name, email=email, phone=phone, telegram=telegram, **extra_fields)

#             if password:
#                 user.set_password(password)
#             else:
#                 user.set_unusable_password()

#             user.save(using=self._db)

#             group, _ = Group.objects.get_or_create(name="Користувачі")
#             user.groups.add(group)

#         return user

#     def create_superuser(self, name, email, password, **extra_fields):
#         extra_fields.setdefault("is_staff", True)
#         extra_fields.setdefault("is_superuser", True)
#         return self.create_user(name=name, email=email, password=password, **extra_fields)

phone_validator = RegexValidator(
    regex=r"^\+\d{1,15}$",
    message="Phone number must be in international format (e.g., +380123456789)",
 )
# Custom User Model
class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=100, null=False, blank=False)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.CharField(max_length=20, unique=True, blank=True, null=True, validators=[phone_validator])
    telegram = models.CharField(max_length=50, unique=True, null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]
    
    def __str__(self):
        return self.email or self.phone or self.telegram

    def get_tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

# OTP Model
class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = str(random.randint(100000, 999999))
        super().save(*args, **kwargs)



