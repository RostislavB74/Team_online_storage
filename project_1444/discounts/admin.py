from django.contrib import admin
from .models import PromoCode, Coupon

@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ("code", "discount_percentage", "valid_from", "valid_to", "is_active", "usage_limit", "used_count")
    search_fields = ("code",)
    list_filter = ("is_active", "valid_from", "valid_to")
    verbose_name = "Промокоди"
    verbose_name_plural = "Промокоди"

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ("user", "discount_percentage", "valid_from", "valid_to", "is_active")
    list_filter = ("is_active", "valid_from", "valid_to")
    search_fields = ("user__email",)
    verbose_name = "Купони на знижку"
    verbose_name_plural = "Купони на знижку"
