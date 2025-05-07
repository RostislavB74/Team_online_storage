from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import *


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "discount_type",
        "discount_percent",
        "combine_with_others",
        "valid_from",
        "valid_to",
        "is_active",
    )
    list_filter = ("is_active", "valid_from", "valid_to")
    search_fields = ("product__name", "material__material", "status__status")

    verbose_name = _("Знижка")
    verbose_name_plural = _("Знижки")


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "discount_percentage",
        "valid_from",
        "valid_to",
        "is_active",
        "usage_limit",
        "used_count",
    )
    search_fields = ("code",)
    list_filter = ("is_active", "valid_from", "valid_to")
    filter_horizontal = ("applicable_products", "applicable_categories")
    verbose_name = _("Промокоди")
    verbose_name_plural = _("Промокоди")


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = (
        "profile",
        "discount_percentage",
        "valid_from",
        "valid_to",
        "is_active",
    )
    list_filter = ("is_active", "valid_from", "valid_to")
    search_fields = ("user__email",)

    verbose_name = _("Купони на знижку")
    verbose_name_plural = _("Купони на знижку")


@admin.register(PersonalDiscount)
class PersonalDiscountAdmin(admin.ModelAdmin):
    list_display = (
        "profile",
        "discount_percentage",
        "valid_from",
        "valid_to",
        "is_active",
    )
    list_filter = ("is_active", "valid_from", "valid_to")
    search_fields = ("user__email",)

    verbose_name = _("Персональні знижки")
    verbose_name_plural = _("Персональні знижки")


@admin.register(BirthdayDiscount)
class BirthdayDiscountAdmin(admin.ModelAdmin):
    list_display = (
        "profile",
        "discount_percentage",
        "valid_days",
    )
    list_filter = ("valid_days",)

    search_fields = ("user__email",)

    verbose_name = _("Знижки на день народження")
    verbose_name_plural = _("Знижки на день народження")


@admin.register(ProductDiscount)
class ProductDiscountAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "discount_percentage",
        "valid_from",
        "valid_to",
        "is_active",
    )
    list_filter = ("is_active", "valid_from", "valid_to")
    search_fields = ("product__name",)

    verbose_name = _("Знижки на продукти")
    verbose_name_plural = _("Знижки на продукти")


@admin.register(MaterialDiscount)
class MaterialDiscountAdmin(admin.ModelAdmin):
    list_display = (
        "material",
        "discount_percentage",
        "valid_from",
        "valid_to",
        "is_active",
    )
    list_filter = ("is_active", "valid_from", "valid_to")
    search_fields = ("material__name",)

    verbose_name = _("Знижки на матеріали")
    verbose_name_plural = _("Знижки на матеріали")


@admin.register(StatusDiscount)
class StatusDiscountAdmin(admin.ModelAdmin):
    list_display = (
        "status",
        "discount_percentage",
        "valid_from",
        "valid_to",
        "is_active",
    )
    list_filter = ("is_active", "valid_from", "valid_to")
    search_fields = ("status__name",)

    verbose_name = _("Знижки на статуси")
    verbose_name_plural = _("Знижки на статуси")


@admin.register(GemstoneDiscount)
class GemstoneDiscountAdmin(admin.ModelAdmin):
    list_display = (
        "gemstone",
        "discount_percentage",
        "valid_from",
        "valid_to",
        "is_active",
    )
    list_filter = ("is_active", "valid_from", "valid_to")
    search_fields = ("gemstone__name",)

    verbose_name = _("Знижки на камінь")
    verbose_name_plural = _("Знижки на камені")


@admin.register(CollectionDiscount)
class CollectionDiscountAdmin(admin.ModelAdmin):
    list_display = (
        "collection",
        "discount_percentage",
        "valid_from",
        "valid_to",
        "is_active",
    )
    list_filter = ("is_active", "valid_from", "valid_to")
    search_fields = ("collection__name",)

    verbose_name = _("Знижки на колекції")
    verbose_name_plural = _("Знижки на колекції")


@admin.register(OccasionsDiscount)
class OccasionsDiscountAdmin(admin.ModelAdmin):
    list_display = (
        "occasions",
        "discount_percentage",
        "valid_from",
        "valid_to",
        "is_active",
    )
    list_filter = ("is_active", "valid_from", "valid_to")
    search_fields = ("occasions__name",)

    verbose_name = _("Знижки з приводу")
    verbose_name_plural = _("Знижки з приводів")
