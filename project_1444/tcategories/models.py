from django.core.cache import cache
from django.db import models
from django.utils.translation import gettext as _, get_language
from parler.models import TranslatableModel, TranslatedFields

from product.utils import save_with_translation


class TCategories(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=255, unique=True),
        slug=models.SlugField(max_length=255, unique=True, blank=True, null=True),
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="children",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("T категорія виробу")
        verbose_name_plural = _("T категорії виробів")
        ordering = ("-parent_id", "id")

    def __str__(self):
        field_translated = self.safe_translation_getter("name", default=_("Без назви"))
        return f"{self.pk:03d}-{field_translated}"

    def get_cache_key(self, lang=None):
        lang = lang or getattr(self, "language_code", get_language())
        return f"category_{self.pk}_{lang}"

    def clear_cache(self):
        cache.delete(self.get_cache_key())

    def get_full_path(self, lang=None):
        """
        Recursively build the full path of categories with parents.
        Example: 'cat-1/cat-1-1' in user's language
        """

        cache_key = self.get_cache_key(lang)
        # full_path = cache.get(cache_key)
        full_path = None

        if not full_path:
            name = getattr(self, "name", None)
            if self.parent:
                full_path = f"{self.parent.get_full_path()}/{name}"
            else:
                full_path = name
            cache.set(cache_key, full_path, 3600)  # Cache for 1 hour
            print("set full_path", full_path, cache_key)

        return full_path

    def save(self, *args, **kwargs):
        save_with_translation(self, *args, **kwargs)
        self.clear_cache()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.clear_cache()
