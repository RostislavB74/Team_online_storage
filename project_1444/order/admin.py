# from django.utils.html import format_html
# from django.contrib import admin
# from .models import Order, OrderItem
# from django.contrib import admin
# from .models import Order

# admin.site.register(Order)
# admin.site.register(OrderItem)
from django.contrib import admin
from .models import Order, OrderItem

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "total_price", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("user__email", "user__username", "recipient_name", "recipient_phone")
    readonly_fields = ("total_price", "created_at")

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "quantity", "product_price")
    search_fields = ("product__name", "order__user__username")
