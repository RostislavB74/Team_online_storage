import logging

from django.core.cache import cache
from django.db import models
from django.utils.translation import gettext as _, get_language
from parler.models import TranslatableModel, TranslatedFields

from product.utils import save_with_translation

logger = logging.getLogger(__name__)


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
        # field_translated = getattr(self, "name")
        return f"{self.pk:03d}-{field_translated}"

    def get_cache_key(self, lang=None):
        lang = lang or get_language() or getattr(self, "language_code", get_language())
        return f"category_{self.pk}_{lang}"

    def clear_cache(self, lang=None):
        lang = lang or getattr(self, "language_code", get_language())
        # Clear own cache
        cache_key = self.get_cache_key(lang)
        result = cache.delete(cache_key)
        logger.debug(f"clear cache: {cache_key} {result=}")

        # Clear cache for all children
        for child in self.children.all():
            child.clear_cache(lang)

    def get_full_path(self, lang=None):
        """
        Recursively build the full path of categories with parents.
        Example: 'cat-1/cat-1-1' in user's language
        """
        lang = lang or getattr(self, "language_code", get_language())
        cache_key = self.get_cache_key(lang)
        full_path = cache.get(cache_key)
        # full_path = None

        if not full_path:
            name = self.safe_translation_getter(
                "name", default=self.pk, language_code=lang
            )
            if self.parent:
                full_path = f"{self.parent.get_full_path(lang)}/{name}"
            else:
                full_path = name
            cache.set(cache_key, full_path, 3600)  # Cache for 1 hour
            # logger.debug("set full_path : %s, %s", full_path, cache_key)
        # logger.debug("get full_path : %s, %s", full_path, cache_key)
        return full_path

    def save(self, *args, **kwargs):
        save_with_translation(self, *args, **kwargs)
        self.clear_cache()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.clear_cache()
