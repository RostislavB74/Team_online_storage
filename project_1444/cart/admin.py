from django.contrib import admin
from .models import Cart
# from product.models import SubProducts

class CartTabAdmin(admin.TabularInline):
    model = Cart
    fields = ("product", "quantity", "product_price", "product_sum","created_timestamp") 
    search_fields = ("product__name", "quantity", "created_timestamp") 
    readonly_fields = ("created_timestamp", "product_price")  
    extra = 1
    fieldsets = (
        ("Товари в корзині", {
            "fields": (
                "product", "product_price", "quantity", "created_timestamp" 
            ),
        }),
        ("Загальна вартість корзини", {
            "fields": (
                "product_sum",
            )
        })
    )
   

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


