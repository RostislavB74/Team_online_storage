from django.contrib import admin
from .models import Cart
from product.models import SubProducts

class CartTabAdmin(admin.TabularInline):
    model = Cart
    fields = ("product", "quantity", "product_price", "created_timestamp") 
    search_fields = ("product__name", "quantity", "created_timestamp") 
    readonly_fields = ("created_timestamp", "product_price")  
    extra = 1

    def product_price(self, obj):
        return obj.product.price()
    
    # product_price.short_description = "Ціна товара"  # Назва стовпця в адмінці


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ["user_display", "product_display",  "product_price", "quantity", "product_sum", "created_timestamp"]
    list_filter = ["created_timestamp", "user"]

    def user_display(self, obj):
        return str(obj.user) if obj.user else "Анонімний користувач"

    def product_display(self, obj):
        return str(obj.product)

    def product_price(self, obj):
        return obj.product.price
    def product_sum(self, obj):
        return obj.product.price * obj.quantity
    
    user_display.short_description = "Користувач"
    product_display.short_description = "Товар"
    product_price.short_description = "Ціна товару"
    product_sum.short_description = "Сума"



# from django.contrib import admin
# from .models import Cart
# from product.models import SubProducts

# class CartTabAdmin(admin.TabularInline):
#     model = Cart
#     fields = "product", "quantity",'SubProducts.price', "created_timestamp", 
#     search_fields = "product", "quantity", "created_timestamp"
#     readonly_fields = ("created_timestamp",'SubProducts.price',)
#     extra = 1


# @admin.register(Cart)
# class CartAdmin(admin.ModelAdmin):
#     list_display = ["user_display", "product_display", "quantity", "created_timestamp",]
    
#     list_filter = ["created_timestamp", "user",]

#     def user_display(self, obj):
#         if obj.user:
#             return str(obj.user)
#         return "Анонимный пользователь"

#     def product_display(self, obj):
#         return str(obj.product)

#     # user_display and product_display alter name of columns in admin panel
#     user_display.short_description = "Пользователь"
#     product_display.short_description = "Товар"



# @admin.register(Cart)
# class CartAdmin(admin.ModelAdmin):
#     list_display = ("user", "created_at")
#     search_fields = ("user__email", "user__username")

# @admin.register(CartItem)
# class CartItemAdmin(admin.ModelAdmin):
#     list_display = ("cart", "product", "quantity")
#     search_fields = ("product__name", "cart__user__username")

