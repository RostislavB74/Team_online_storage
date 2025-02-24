from django.contrib import admin
from .models import Cart, CartItem

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at")
    search_fields = ("user__email", "user__username")

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("cart", "product", "quantity")
    search_fields = ("product__name", "cart__user__username")

# from django.utils.html import format_html
# from django.contrib import admin
# from .models import Cart, CartItem

# admin.site.register(Cart)
# # @admin.register(Cart)
# # class CartAdmin(admin.ModelAdmin):
# #     list_display = ('user', 'total_price')
# #     list_filter = ('user',)
# #     search_fields = ('user__name',)