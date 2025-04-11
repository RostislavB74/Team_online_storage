from django.contrib import admin
from .models import *
@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ("name","discount_type","discount_percent", "combine_with_others","valid_from", "valid_to", "is_active")
    list_filter = ("is_active", "valid_from", "valid_to")
    search_fields = ("product__name", "material__material", "status__status")
@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ("code", "discount_percentage", "valid_from", "valid_to", "is_active", "usage_limit", "used_count")
    search_fields = ("code",)
    list_filter = ("is_active", "valid_from", "valid_to")
    filter_horizontal=("applicable_products", "applicable_categories")
    verbose_name = "Промокоди"
    verbose_name_plural = "Промокоди"

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ("user", "discount_percentage", "valid_from", "valid_to", "is_active")
    list_filter = ("is_active", "valid_from", "valid_to")
    search_fields = ("user__email",)
    
    verbose_name = "Купони на знижку"
    verbose_name_plural = "Купони на знижку"
@admin.register(PersonalDiscount)
class PersonalDiscountAdmin(admin.ModelAdmin):
    list_display = ("user", "discount_percentage", "valid_from", "valid_to", "is_active")
    list_filter = ("is_active", "valid_from", "valid_to")
    search_fields = ("user__email",)    

    verbose_name = "Персональні знижки"
    verbose_name_plural = "Персональні знижки"

@admin.register(BirthdayDiscount)
class BirthdayDiscountAdmin(admin.ModelAdmin):
    list_display = ("user", "discount_percentage", "valid_days",)
    list_filter = ("valid_days",)
    
    search_fields = ("user__email",)

    verbose_name = "Знижки на день народження"
    verbose_name_plural = "Знижки на день народження"
@admin.register(ProductDiscount)
class ProductDiscountAdmin(admin.ModelAdmin):    
    list_display = ("product", "discount_percentage", "valid_from", "valid_to", "is_active")
    list_filter = ("is_active", "valid_from", "valid_to")
    search_fields = ("product__name",)

    verbose_name = "Знижки на продукти"
    verbose_name_plural = "Знижки на продукти"

@admin.register(MaterialDiscount)
class MaterialDiscountAdmin(admin.ModelAdmin):    
    list_display = ("material", "discount_percentage", "valid_from", "valid_to", "is_active")
    list_filter = ("is_active", "valid_from", "valid_to")
    search_fields = ("material__name",)

    verbose_name = "Знижки на матеріали"
    verbose_name_plural = "Знижки на матеріали"

@admin.register(StatusDiscount)
class StatusDiscountAdmin(admin.ModelAdmin):    
    list_display = ("status", "discount_percentage", "valid_from", "valid_to", "is_active")
    list_filter = ("is_active", "valid_from", "valid_to")
    search_fields = ("status__name",)

    verbose_name = "Знижки на статуси"
    verbose_name_plural = "Знижки на статуси"

@admin.register(GemstoneDiscount)
class GemstoneDiscountAdmin(admin.ModelAdmin):    
    list_display = ("gemstone", "discount_percentage", "valid_from", "valid_to", "is_active")
    list_filter = ("is_active", "valid_from", "valid_to")
    search_fields = ("gemstone__name",)

    verbose_name = "Знижки на камінь"
    verbose_name_plural = "Знижки на камені"
@admin.register(CollectionDiscount)
class CollectionDiscountAdmin(admin.ModelAdmin):    
    list_display = ("collection", "discount_percentage", "valid_from", "valid_to", "is_active")
    list_filter = ("is_active", "valid_from", "valid_to")
    search_fields = ("collection__name",)

    verbose_name = "Знижки на колекції"
    verbose_name_plural = "Знижки на колекції"
# @admin.register(SeasonDiscount)
# class SeasonDiscountAdmin(admin.ModelAdmin):
#     list_display = ("season", "discount_percentage", "valid_from", "valid_to", "is_active")
#     list_filter = ("is_active", "valid_from", "valid_to")
#     search_fields = ("season__name",)

#     verbose_name = "Знижки на сезон"
#     verbose_name_plural = "Знижки на сезон"
@admin.register(OccasionsDiscount)
class OccasionsDiscountAdmin(admin.ModelAdmin):
    list_display = ("ocassions", "discount_percentage", "valid_from", "valid_to", "is_active")
    list_filter = ("is_active", "valid_from", "valid_to")
    search_fields = ("ocassions__name",)

    verbose_name = "Знижки з приводу"
    verbose_name_plural = "Знижки з приводів"