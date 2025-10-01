from django.db import models
from django.db.models.enums import StrEnum
from django.utils.translation import gettext_lazy as _


class GenderChoices(models.TextChoices):
    MALE = "M", _("Male")
    FEMALE = "F", _("Female")
    UNDEFINED = "U", _("Undefined")


class OTPStatus(StrEnum):
    SUCCESS = "success"
    ERROR = "error"
    SENT = "otp_sent"
    DISABLED = "disabled"
