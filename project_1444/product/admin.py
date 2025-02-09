from django.utils.html import format_html
from django.contrib import admin
from .models import (
    Category, Material,  Gemstone, Product, 
    ProductImage, ProductCertificate, RingSizeConversion
)

@admin.register(RingSizeConversion)
class RingSizeAdmin(admin.ModelAdmin):
    list_display = ('circumference_mm', 'diameter_mm', 'size_ua', 'size_us', 'size_eu', 'size_uk', 'size_asia', 'size_other_eu')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent',)
    search_fields = ('name',)

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('article','name','color', 'assay','type', )
    list_filter = ('article','name','color', 'assay','type',)
    search_fields = ('article','name','color', 'assay','type', )
    list_display_links = ('article','name','color', 'assay','type', )


@admin.register(Gemstone)
class GemstoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'color','origin_stone')
    list_filter = ('name', 'type', 'color',)
    search_fields = ('name','color', 'type', )
    list_display_links = ('name','color','type', )


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # Дозволяє додати 1 нове зображення вручну (не створюється автоматично)

# Інлайн-клас для додавання сертифікатів безпосередньо в товар
class ProductCertificateInline(admin.TabularInline):
    model = ProductCertificate
    extra = 1

# Налаштування для товару
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    readonly_fields = ('sku', 'article', 'qr_code', 'created_at', 'updated_at', 'created_by')
    list_display = ('article', 'sku', 'name', 'category', 'material', 'weight_material', 'ean_13')
    list_filter = ('category', 'material', 'coating', 'gold_plates')
    search_fields = ('name', 'sku', 'ean_13')
    inlines = [ProductImageInline, ProductCertificateInline]

    def get_images(self, obj):
        """Показує перше зображення товару в списку товарів"""
        first_image = obj.images.first()
        if first_image:
            return format_html('<img src="{}" width="50" height="50" />', first_image.image.url)
        return "Немає зображень"

    get_images.short_description = "Зображення"

# Окремий адмін для зображень товару
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'product_article', 'product_name', 'preview')
    search_fields = ('product__article', 'product__name')

    def product_article(self, obj):
        return obj.product.article
    product_article.short_description = "Артикул"

    def product_name(self, obj):
        return obj.product.name
    product_name.short_description = "Назва"

    def preview(self, obj):
        return format_html('<img src="{}" width="50" height="50" />', obj.image.url) if obj.image else "Немає зображення"
    preview.short_description = "Зображення"

# Окремий адмін для сертифікатів товару
@admin.register(ProductCertificate)
class ProductCertificateAdmin(admin.ModelAdmin):
    list_display = ('product', 'product_article', 'product_name', 'file_link')
    search_fields = ('product__article', 'product__name')

    def product_article(self, obj):
        return obj.product.article
    product_article.short_description = "Артикул"

    def product_name(self, obj):
        return obj.product.name
    product_name.short_description = "Назва"

    def file_link(self, obj):
        return format_html('<a href="{}" target="_blank">Переглянути</a>', obj.file.url) if obj.file else "Немає сертифіката"
    file_link.short_description = "Сертифікат"

    