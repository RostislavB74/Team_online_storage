from django.utils.html import format_html
from django.contrib import admin
from .models import (
    Categories, Material, Gemstone, Product, SubCategories,
    ProductImage, ProductCertificate, RingSizeConversion, Occasion, RingSizeConversion,Colors,
    ProductGemstone,  ProductAttributes,  Collections, ProductMaterial
)
from parler.admin import TranslatableAdmin
from django.contrib import admin
from django.utils.html import format_html
from parler.admin import TranslatableAdmin, TranslatableTabularInline
from django.utils.html import format_html


@admin.register(RingSizeConversion)
class RingSizeAdmin(admin.ModelAdmin):
    list_display = ('circumference_mm', 'diameter_mm', 
                    'size_ua', 'size_us', 'size_eu', 
                    'size_uk', 'size_asia', 'size_other_eu')


@admin.register(Categories)
class CategoriesAdmin(TranslatableAdmin):
    list_display = ('name', 'slug')
    
    def get_prepopulated_fields(self, request, obj=None):
        return {'slug': ('name',)}

@admin.register(Colors)
class ColorsAdmin(TranslatableAdmin):
    list_display = ('name', 'slug')
    
    def get_prepopulated_fields(self, request, obj=None):
        return {'slug': ('name',)}
@admin.register(Collections)
class CollectionsAdmin(TranslatableAdmin):
    list_display = ('name', 'slug')
    
    def get_prepopulated_fields(self, request, obj=None):
        return {'slug': ('name',)}
@admin.register(SubCategories)
class SubCategoriesAdmin(TranslatableAdmin):
    list_display = ('name', 'slug', )
    search_fields = ('name',)
    def get_prepopulated_fields(self, request, obj=None):
        return {'slug': ('name',)}


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('article', 'material', 'color', 'assay',)
    search_fields = ('article', 'material','color', 'assay',)
    list_display_links = ('material','color', 'assay',)


@admin.register(Gemstone)
class GemstoneAdmin(TranslatableAdmin):
    list_display = ('name', 'slug', 'type', 'color', 'origin_stone')
    search_fields = ('name', 'color', 'type',)
    list_display_links = ('name', 'color', 'type',)
    def get_prepopulated_fields(self, request, obj=None):
        return {'slug': ('name',)}


# Інлайн для зображень товару
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


# Інлайн для сертифікатів товару
class ProductCertificateInline(admin.TabularInline):
    model = ProductCertificate
    extra = 1
class ProductAttributesInline(TranslatableTabularInline):
    model = ProductAttributes
    extra = 1  
    fields = ("gender", "color_coating","clasp_type", "coating_material", "description_coating", "design_product", "style", "status")
    verbose_name = "Характеристики"
    verbose_name_plural = "Характеристики"

class ProductGemstoneInline(admin.TabularInline):
    model = ProductGemstone
    extra = 1
    fields=("gemstone", "is_main", "color")
    verbose_name = "Камінь"
    verbose_name_plural = "Камені"
class ProductMaterialInline(admin.TabularInline):
    model = ProductMaterial
    extra = 1
    fields=("material", "is_primary")
    verbose_name = "Матеріал"
    verbose_name_plural = "Матеріали"
# Налаштування для товару
@admin.register(Product)
class ProductAdmin(TranslatableAdmin):
    list_display = ('article', 'sku', 'category','name',  'slug', "display_attributes", 'weight_material', 'ean_13', 'get_images','display_qr_code', 'get_certificates',)
    search_fields = ('name', 'sku', 'ean_13', 'category__name', 'material__name', 'gemstone__name','coating', 'gold_plates',)
    readonly_fields = ('sku', 'article', 'qr_code', 'created_at', 'updated_at', 'created_by',)
    filter_horizontal = ('occasions',)
    inlines = [ProductMaterialInline, ProductImageInline, ProductCertificateInline, ProductAttributesInline, ProductGemstoneInline]
    fieldsets = (
        ("Основна інформація", {
            "fields": ("category","subcategory","name","article", "ean_13", "sku", "slug"),
            "classes": ("collapse",),
        }),
        
        ("Ціна та знижки", {
            "fields": ("price", "discount_percentage", "new_price", "old_price"),
            "classes": ("collapse",),  # Згортає блок
        }),
        ("Розміри та характеристики", {
            "fields": ("size", "circumference_mm", "dimensions", "width_mm", "length_mm", "weight_material",),
            "classes": ("collapse",),
        }),
        # ("Камені", {
        #     "fields": ("main_set_included", ),
        #     "classes": ("collapse",),
        # }),
        ("Додаткові параметри", {
            "fields": ("collection", "year_collection", "country_of_origin", "occasions", "coating", "gold_plates"),
            "classes": ("collapse",),
        }),
        ("Медіа", {
            "fields": ("qr_code",),
            "classes": ("collapse",),
        }),
        ("Системні поля", {
            "fields": ("created_by", "created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )
    def display_attributes(self, obj):
       
        if hasattr(obj, "attributes"):  # Перевіряємо, чи є у товару атрибути
            attr = obj.attributes  # Отримуємо єдиний об'єкт атрибутів
            attributes_list = [
                f"Стать: {attr.get_gender_display()}",
                f"Колір покриття: {attr.color_coating}" if attr.color_coating else "",
                f"Тип застібки: {attr.clasp_type}" if attr.clasp_type else "",
                f"Матеріал покриття: {attr.coating_material}" if attr.coating_material else "",
                f"Опис покриття: {attr.description_coating}" if attr.description_coating else "",
                f"Дизайн: {attr.design_product}" if attr.design_product else "",
                f"Стиль: {attr.style}" if attr.style else "",
                f"Статус: {attr.status}" if attr.status else "",
            ]
            return format_html("<br>".join([a for a in attributes_list if a]))  # Видаляємо порожні значення

        return "Немає характеристик"
        # attributes = obj.attributes  
        # return format_html("<br>".join([f"{attr.attribute_name}: {attr.value}" for attr in attributes]))

    display_attributes.short_description = "Додаткові характеристики"
    def display_qr_code(self, obj):
        if obj.qr_code:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 5px;" />', obj.qr_code.url)
        return "Немає зображення"

    display_qr_code.short_description = "QR-код"
    def get_prepopulated_fields(self, request, obj=None):
        return {'slug': ('name',)}
    
    
    def get_images(self, obj):
        """Показує перше зображення товару в списку товарів"""
        first_image = obj.images.first()
        if first_image and first_image.image:
            return format_html('<img src="{}" width="50" height="50" />', first_image.image.url)
        return "Немає зображень"

    get_images.short_description = "Зображення"

    def get_certificates(self, obj):
        """Показує посилання на перший сертифікат товару"""
        first_certificate = obj.certificates.first()
        if first_certificate and first_certificate.file:
            return format_html('<a href="{}" target="_blank">Сертифікат</a>', first_certificate.file.url)
        return "Немає сертифікатів"

    get_certificates.short_description = "Сертифікати"
    

    
# Адмінка для подій (на які випадки можна дарувати товар)
@admin.register(Occasion)
class OccasionAdmin(TranslatableAdmin):
    list_display = ('name', 'slug')
    
    def get_prepopulated_fields(self, request, obj=None):
        return {'slug': ('name',)}


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
