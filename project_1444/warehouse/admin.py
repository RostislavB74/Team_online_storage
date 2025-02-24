from django.contrib import admin
from .models import Warehouse, WarehouseStock, Reservation
# Register your models here.

# admin.site.register(Warehouse)
# admin.site.register(WarehouseStock)
# admin.site.register(Reservation)


class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'phone')
    list_display_links = ('name', 'location')
    search_fields = ('name', 'location', 'phone')

class WarehouseStockAdmin(admin.ModelAdmin):
    list_display = ('warehouse', 'product', 'quantity')
    list_display_links = ('warehouse', 'product')
    search_fields = ('warehouse', 'product')

class ReservationAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'warehouse')
    list_display_links = ('product', 'quantity', 'warehouse')
    search_fields = ('product', 'quantity', 'warehouse')

admin.site.register(Warehouse, WarehouseAdmin)
admin.site.register(WarehouseStock, WarehouseStockAdmin)
admin.site.register(Reservation, ReservationAdmin)

