from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from parler.admin import TranslatableAdmin

from product.models import (
    Categories,
    Material,
    Gemstone,
    Product,
    SubCategories,
    TypeGemstones,
    Origin,
    ProductImage,
    ProductCertificate,
    Occasion,
    RingSizeConversion,
    Colors,
    ProductGemstone,
    ProductAttributes,
    Collections,
    ProductMaterial,
    ProductStatus,
    SubProducts,
    Designs,
    Weaving,
    Clasp,
    Coating,
    Styles,
    Descriptions,
)


@admin.register(Descriptions)
class DescriptionsAdmin(TranslatableAdmin):
    list_display = (
        "get_name",
        "get_slug",
        "get_text",
        "get_seo_title",
        "get_seo_description",
        "get_keywords",
    )
    search_fields = ("translations__name", "translations__text", "translations__slug")
    list_display_links = (
        "get_name",
        "get_text",
    )

    def get_name(self, obj):
        return obj.safe_translation_getter("name", default=_("Unnamed"))

    def get_slug(self, obj):
        return obj.safe_translation_getter("slug", default=_("No slug"))

    def get_text(self, obj):
        return obj.safe_translation_getter("text", default=_("No text"))

    def get_seo_title(self, obj):
        return obj.safe_translation_getter("seo_title", default=_("No SEO title"))

    def get_seo_description(self, obj):
        return obj.safe_translation_getter(
            "seo_description", default=_("No SEO description")
        )

    def get_keywords(self, obj):
        return obj.safe_translation_getter("keywords", default=_("No keywords"))

    get_name.admin_order_field = "translations__name"
    get_name.short_description = _("Name")

    get_slug.admin_order_field = "translations__slug"
    get_slug.short_description = _("Slug")

    get_text.admin_order_field = "translations__text"
    get_text.short_description = _("Text")

    get_seo_title.admin_order_field = "translations__seo_title"
    get_seo_title.short_description = _("SEO Title")

    get_seo_description.admin_order_field = "translations__seo_description"
    get_seo_description.short_description = _("SEO Description")

    get_keywords.admin_order_field = "translations__keywords"
    get_keywords.short_description = _("Keywords")


@admin.register(Gemstone)
class GemstoneAdmin(TranslatableAdmin):
    list_display = ("get_name", "slug", "get_type", "get_origin", "level")
    search_fields = (
        "translations__name",
        "type",
    )
    list_display_links = (
        "get_name",
        "get_type",
    )

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
        return {"slug": ("name",)}


@admin.register(ProductStatus)
class ProductStatusAdmin(TranslatableAdmin):
    list_display = ("name", "slug")

    def get_prepopulated_fields(self, request, obj=None):
        return {"slug": ("name",)}


@admin.register(RingSizeConversion)
class RingSizeAdmin(admin.ModelAdmin):
    list_display = (
        "circumference_mm",
        "diameter_mm",
        "size_ua",
        "size_us",
        "size_eu",
        "size_uk",
        "size_asia",
        "size_other_eu",
    )


@admin.register(Categories)
class CategoriesAdmin(TranslatableAdmin):
    list_display = ("id", "name", "slug")

    def get_prepopulated_fields(self, request, obj=None):
        return {"slug": ("name",)}


@admin.register(Colors)
class ColorsAdmin(TranslatableAdmin):
    list_display = ("name", "slug")

    def get_prepopulated_fields(self, request, obj=None):
        return {"slug": ("name",)}


@admin.register(Styles)
class StylesAdmin(TranslatableAdmin):
    list_display = ("name", "slug")

    def get_prepopulated_fields(self, request, obj=None):
        return {"slug": ("name",)}


@admin.register(Coating)
class CoatingAdmin(TranslatableAdmin):
    list_display = ("name", "slug")

    def get_prepopulated_fields(self, request, obj=None):
        return {"slug": ("name",)}


@admin.register(Clasp)
class ClaspAdmin(TranslatableAdmin):
    list_display = ("name", "slug")

    def get_prepopulated_fields(self, request, obj=None):
        return {"slug": ("name",)}


@admin.register(Weaving)
class WeavingAdmin(TranslatableAdmin):
    list_display = ("name", "slug")

    def get_prepopulated_fields(self, request, obj=None):
        return {"slug": ("name",)}


@admin.register(Designs)
class DesignsAdmin(TranslatableAdmin):
    list_display = ("name", "slug")

    def get_prepopulated_fields(self, request, obj=None):
        return {"slug": ("name",)}


@admin.register(Collections)
class CollectionsAdmin(TranslatableAdmin):
    list_display = ("name", "slug")

    def get_prepopulated_fields(self, request, obj=None):
        return {"slug": ("name",)}


@admin.register(SubCategories)
class SubCategoriesAdmin(TranslatableAdmin):
    list_display = (
        "id",
        "name",
        "slug",
    )
    search_fields = ("name",)

    def get_prepopulated_fields(self, request, obj=None):
        return {"slug": ("name",)}


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "article",
        "material",
        "color",
        "assay",
    )
    search_fields = (
        "article",
        "material",
        "color",
        "assay",
    )
    readonly_fields = ("article",)
    list_display_links = (
        "material",
        "color",
        "assay",
    )


# Інлайн для зображень товару
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


# Інлайн для сертифікатів товару
class ProductCertificateInline(admin.TabularInline):
    model = ProductCertificate
    extra = 1


class ProductAttributesInline(admin.TabularInline):
    model = ProductAttributes
    extra = 1
    fields = (
        "gender",
        "color_coating",
        "clasp_type",
        "coating_material",
        "weaving_type",
        "style",
    )

    verbose_name = _("Характеристики")
    verbose_name_plural = _("Характеристики")


class ProductGemstoneInline(admin.TabularInline):
    model = ProductGemstone
    extra = 1
    fields = ("gemstone", "is_main", "color")
    verbose_name = _("Камінь")
    verbose_name_plural = _("Камені")


class ProductMaterialInline(admin.TabularInline):
    model = ProductMaterial
    extra = 1
    fields = ("material", "is_primary")
    verbose_name = _("Матеріал")
    verbose_name_plural = _("Матеріали")


# Налаштування для товару
@admin.register(SubProducts)
class SubProductsAdmin(admin.ModelAdmin):
    list_display = (
        "article",
        "sku",
        "id",
        "parent_product",
        "ean_13",
        "size",
        "weight",
        "length",
        "max_length",
        "width",
        "size",
        "price",
        "discount_percentage",
        "new_price",
        "old_price",
        "created_by",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "position",
        "sku",
        "ean_13",
    )
    readonly_fields = (
        "sku",
        "article",
        "qr_code",
        "id",
        "created_at",
        "updated_at",
        "created_by",
    )
    actions = [
        "mark_as_bestseller",
        "remove_bestseller",
        "mark_as_discount",
        "remove_discount",
    ]

    fieldsets = (
        (
            _("Основна інформація"),
            {
                "fields": (
                    "article",
                    "ean_13",
                    "sku",
                    "parent_product",
                    "id",
                    "size",
                    "length",
                    "max_length",
                    "width",
                    "weight",
                    "price",
                ),
            },
        ),
        (
            _("Ціна та знижки"),
            {
                "fields": ("discount_percentage", "new_price", "old_price"),
            },
        ),
        (
            _("Системні поля"),
            {
                "fields": ("created_by", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    @admin.action(description=_("Позначити як знижка"))
    def mark_as_discount(self, request, queryset):
        discount_status, _ = ProductStatus.objects.get_or_create(name="discount")
        for product in queryset:
            product.statuses.add(discount_status)
        self.message_user(request, _("Вибрані товари отримали статус 'discount'."))

    @admin.action(description=_("Прибрати статус знижки"))
    def remove_discount(self, request, queryset):
        discount_status = ProductStatus.objects.filter(name="discount").first()
        if discount_status:
            for product in queryset:
                product.statuses.remove(discount_status)
        self.message_user(request, _("Статус 'discount' видалено у вибраних товарів."))


@admin.register(Occasion)
class OccasionAdmin(TranslatableAdmin):
    list_display = ("name", "slug")

    def get_prepopulated_fields(self, request, obj=None):
        return {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(TranslatableAdmin):
    list_display = (
        "article",
        "sku",
        "category",
        "subcategory",
        "name",
        "slug",
        "ean_13",
        "get_images",
        "get_certificates",
    )
    search_fields = ("name", "sku", "ean_13", "category__name", "subcategory__name")
    readonly_fields = (
        "sku",
        "article",
        "created_at",
        "updated_at",
        "created_by",
    )
    inlines = [
        ProductImageInline,
        ProductMaterialInline,
        ProductGemstoneInline,
        ProductCertificateInline,
        ProductAttributesInline,
    ]
    actions = [
        "mark_as_bestseller",
        "remove_bestseller",
        "mark_as_discount",
        "remove_discount",
    ]
    filter_horizontal = (
        "subproducts",
        "statuses",
        "description",
    )
    fieldsets = (
        (
            _("Основна інформація"),
            {
                "fields": (
                    "category",
                    "subcategory",
                    "name",
                    "article",
                    "ean_13",
                    "sku",
                    "slug",
                    "collection",
                    "year_collection",
                    "design",
                    "country_of_origin",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Статуси",
            {
                "fields": ("statuses",),
                "classes": ("collapse",),
            },
        ),
        (
            _("Опис товару"),
            {
                "fields": ("description",),
                "classes": ("collapse",),
            },
        ),
        (
            _("Типорозміри товару"),
            {
                "fields": ("subproducts",),
                "classes": ("collapse",),
            },
        ),
        (
            _("Системні поля"),
            {
                "fields": ("created_by", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def get_images(self, obj):
        """Показує перше зображення товару в списку товарів"""
        first_image = obj.images.first()
        if first_image and first_image.image:
            return format_html(
                '<img src="{}" width="50" height="50" />', str(first_image.image)
            )
        return _("Немає зображень")

    get_images.short_description = _("Зображення")

    def get_certificates(self, obj):
        """Показує посилання на перший сертифікат товару"""
        first_certificate = obj.certificates.first()
        if first_certificate and first_certificate.file:
            return format_html(
                '<a href="{}" target="_blank">{}</a>',
                str(first_certificate.file),
                _("Сертифікат"),
            )
        return _("Немає сертифікатів")

    get_certificates.short_description = _("Сертифікати")

    @admin.action(description=_("Позначити товари як бестселери"))
    def set_bestseller(self, request, queryset):
        queryset.update(is_bestseller=True)

    @admin.action(description=_("Зняти статус бестселера"))
    def clear_bestseller(self, request, queryset):
        queryset.update(is_bestseller=False)

    def get_statuses(self, obj):
        return ", ".join([status.name for status in obj.status.all()])

    get_statuses.short_description = _("Статуси")

    @admin.action(description=_("Позначити як бестселер"))
    def mark_as_bestseller(self, request, queryset):
        bestseller_status, _ = ProductStatus.objects.get_or_create(name="bestseller")
        for product in queryset:
            product.statuses.add(bestseller_status)
        self.message_user(request, _("Вибрані товари отримали статус 'bestseller'."))

    @admin.action(description=_("Прибрати статус бестселера"))
    def remove_bestseller(self, request, queryset):
        bestseller_status = ProductStatus.objects.filter(name="bestseller").first()
        if bestseller_status:
            for product in queryset:
                product.statuses.remove(bestseller_status)
        self.message_user(
            request, _("Статус 'bestseller' видалено у вибраних товарів.")
        )

    def get_prepopulated_fields(self, request, obj=None):
        return {"slug": ("name",)}


# Адмінка для подій (на які випадки можна дарувати товар)


class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("product", "product_article", "product_name", "preview")
    search_fields = ("product__article", "product__name")

    def product_article(self, obj):
        return obj.product.article

    product_article.short_description = _("Артикул")

    def product_name(self, obj):
        return obj.product.name

    product_name.short_description = _("Назва")

    def preview(self, obj):
        return (
            format_html('<img src="{}" width="50" height="50" />', str(obj.image))
            if obj.image
            else _("Немає зображення")
        )

    preview.short_description = _("Зображення")


# Окремий адмін для сертифікатів товару
@admin.register(ProductCertificate)
class ProductCertificateAdmin(admin.ModelAdmin):
    list_display = ("product", "product_article", "product_name", "file_link")
    search_fields = ("product__article", "product__name")

    def product_article(self, obj):
        return obj.product.article

    product_article.short_description = _("Артикул")

    def product_name(self, obj):
        return obj.product.name

    product_name.short_description = _("Назва")

    def file_link(self, obj):
        return (
            format_html('<a href="{}" target="_blank"></a>', str(obj.file)),
            _("Переглянути") if obj.file else _("Немає сертифіката"),
        )

    file_link.short_description = _("Сертифікат")
