from django.db import models
from django.utils.translation import gettext as _
from parler.models import TranslatableModel, TranslatedFields

from product.utils import save_with_translation


class TCategories(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=255, unique=True),
        slug=models.SlugField(max_length=255, unique=True, blank=True, null=True),
    )
    parent_id = models.IntegerField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        save_with_translation(self, *args, **kwargs)

    class Meta:
        verbose_name = _("T категорія виробу")
        verbose_name_plural = _("T категорії виробів")

    def __str__(self):
        field_translated = self.safe_translation_getter("name", default=_("Без назви"))
        return f"{self.pk:03d}-{field_translated}"
