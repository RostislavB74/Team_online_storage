from django.utils.html import format_html
from django.utils.translation import get_language
from django.shortcuts import get_object_or_404
from django.contrib import admin
from .models import (
    Categories, Material, Gemstone, Product, SubCategories,TypeGemstones, Origin,
    ProductImage, ProductCertificate, RingSizeConversion, Occasion, RingSizeConversion,Colors,
    ProductGemstone,  ProductAttributes,  Collections, ProductMaterial, ProductStatus, SubProducts
)
from parler.admin import TranslatableAdmin
from django.contrib import admin
from django.utils.html import format_html
from parler.admin import TranslatableAdmin, TranslatableTabularInline
from django.utils.html import format_html

from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from parler.admin import TranslatableAdmin
from .models import Gemstone

from django.contrib import admin
from django import forms
from .models import Product

from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from django.utils.html import format_html
from .models import Product

from django.utils import translation

from django.utils.text import slugify


# @admin.register(SizeType)
# class SizeTypeAdmin(admin.ModelAdmin):
#     list_display = ('name',)
#     search_fields = ('name',) 
#     list_display_links = ('name',)

    
@admin.register(Gemstone)
class GemstoneAdmin(TranslatableAdmin):
    list_display = ('get_name', 'slug', 'get_type', 'get_origin', 'level')
    search_fields = ('translations__name',  'type',)
    list_display_links = ('get_name', 'get_type',)

    def get_name(self, obj):
        return obj.safe_translation_getter("name", default=_("Unnamed"))
    get_name.admin_order_field = "translations__name"
    get_name.short_description = _("Name")

    def get_type(self, obj):
        return dict(TypeGemstones.choices).get(obj.type, _("Unknown"))
    get_type.short_description = _("Type")

    def get_origin(self, obj):
        return dict(Origin.choices).get(obj.origin_stone, _("Unknown"))
    get_origin.short_description = _("Origin")

    def get_prepopulated_fields(self, request, obj=None):
        return {'slug': ('name',)}

# @admin.register(ProductSize)
# class ProductSizeAdmin(admin.ModelAdmin):
#     list_display = ('product', 'length', 'width', 'diameter', 'weight',)
#     fields = ('product', 'length', 'width', 'diameter', 'weight',)
#     # fields= ("size", "circumference_mm", "dimensions", "width_mm", "length_mm", "weight_material",)
            

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
    fields = ("gender", "color_coating","clasp_type", "coating_material", "description_coating", "design_product", "style", "statuses")
    
    verbose_name = "Характеристики"
    verbose_name_plural = "Характеристики"
    @admin.action(description="Позначити товари як бестселери")
    def set_bestseller(self, request, queryset):
        queryset.update(is_bestseller=True)

    @admin.action(description="Зняти статус бестселера")
    def clear_bestseller(self, request, queryset):
        queryset.update(is_bestseller=False)
    def get_statuses(self, obj):
        return ", ".join([status.name for status in obj.status.all()])
    get_statuses.short_description = "Статуси"

    @admin.action(description="Позначити як бестселер")
    def mark_as_bestseller(self, request, queryset):
        bestseller_status, _ = ProductStatus.objects.get_or_create(name="bestseller")
        for product in queryset:
            product.statuses.add(bestseller_status)
        self.message_user(request, "Вибрані товари отримали статус 'bestseller'.")

    @admin.action(description="Прибрати статус бестселера")
    def remove_bestseller(self, request, queryset):
        bestseller_status = ProductStatus.objects.filter(name="bestseller").first()
        if bestseller_status:
            for product in queryset:
                product.statuses.remove(bestseller_status)
        self.message_user(request, "Статус 'bestseller' видалено у вибраних товарів.")

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
@admin.register(SubProducts)
class SubProductsAdmin(admin.ModelAdmin):
    list_display = ('article', 'sku', 'position', 'parent_product',"display_attributes", 'ean_13', 'display_qr_code', 'size','weight', 'length', 'width', 'size', 'price','discount_percentage', 'new_price', 'old_price', 'display_qr_code', 'created_by', 'created_at', 'updated_at')
    search_fields = ('position', 'sku', 'ean_13', 'material__name', 'gemstone__name',)
    readonly_fields = ('sku', 'article', 'qr_code','position', 'created_at', 'updated_at', 'created_by',)

    # inlines = [ProductMaterialInline, ProductGemstoneInline]
    actions = ['mark_as_bestseller', 'remove_bestseller', 'mark_as_discount', 'remove_discount']

    fieldsets = (
        ("Основна інформація", {
            "fields": ("article" , "ean_13", "sku",'parent_product' , "position",'size', 'length', 'width', 'weight',"price",  ),
        }),
        
        ("Ціна та знижки", {
            "fields": ("discount_percentage", "new_price", "old_price"),
        }),
        
        ("Системні поля", {
            "fields": ("created_by", "created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    @admin.action(description="Позначити як знижка")
    def mark_as_discount(self, request, queryset):
        discount_status, _ = ProductStatus.objects.get_or_create(name="discount")
        for product in queryset:
            product.statuses.add(discount_status)
        self.message_user(request, "Вибрані товари отримали статус 'discount'.")

    @admin.action(description="Прибрати статус знижки")
    def remove_discount(self, request, queryset):
        discount_status = ProductStatus.objects.filter(name="discount").first()
        if discount_status:
            for product in queryset:
                product.statuses.remove(discount_status)
        self.message_user(request, "Статус 'discount' видалено у вибраних товарів.")
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
                f"Статус: {attr.statuses}" if attr.statuses else "",
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
    
@admin.register(Occasion)
class OccasionAdmin(TranslatableAdmin):
    list_display = ('name', 'slug')
    
    def get_prepopulated_fields(self, request, obj=None):
        return {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(TranslatableAdmin):
    list_display = ('article', 'sku', 'category','subcategory','name', 'slug', 'ean_13','get_images', 'get_certificates', )
    search_fields = ('name', 'sku', 'ean_13', 'category__name', 'subcategory__name')
    readonly_fields = ('sku', 'article', 'created_at', 'updated_at', 'created_by',)
    inlines = [ProductImageInline, ProductMaterialInline, ProductGemstoneInline, ProductCertificateInline,ProductAttributesInline]
    actions = ['mark_as_bestseller', 'remove_bestseller', 'mark_as_discount', 'remove_discount']
    filter_horizontal = ("subproducts",) 
    fieldsets = (
        ("Основна інформація", {
            "fields": ("category","subcategory","name","article" , "ean_13", "sku", "slug","collection", "year_collection", "country_of_origin",),
            "classes": ("collapse",),
        }),
       ("Типорозміри товару", {
            "fields": ("subproducts",),
            "classes": ("collapse",),
        }),
        ("Системні поля", {
            "fields": ("created_by", "created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )
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

    @admin.action(description="Позначити як знижка")
    def mark_as_discount(self, request, queryset):
        discount_status, _ = ProductStatus.objects.get_or_create(name="discount")
        for product in queryset:
            product.statuses.add(discount_status)
        self.message_user(request, "Вибрані товари отримали статус 'discount'.")

    @admin.action(description="Прибрати статус знижки")
    def remove_discount(self, request, queryset):
        discount_status = ProductStatus.objects.filter(name="discount").first()
        if discount_status:
            for product in queryset:
                product.statuses.remove(discount_status)
        self.message_user(request, "Статус 'discount' видалено у вибраних товарів.")
    def get_prepopulated_fields(self, request, obj=None):
        return {'slug': ('name',)}

    
# Адмінка для подій (на які випадки можна дарувати товар)


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
