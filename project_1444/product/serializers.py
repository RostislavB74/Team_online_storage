from rest_framework import serializers
from typing import List  # Для типу List[str]
from drf_spectacular.utils import extend_schema_field

# from django.utils.translation import gettext_lazy as _

from product.models import (
    SubCategories,
    Categories,
    Descriptions,
    Material,
    ProductGemstone,
    ProductMaterial,
    ProductStatus,
    ProductAttributes,
    SubProducts,
    ProductImage,
    ProductCertificate,
    Product,
)
from product.utils import get_discounted_price
from project_1444.settings import (
    CLOUDINARY_IMAGE_FIXED_PREFIX_PATH,
    CLOUDINARY_FILE_FIXED_PREFIX_PATH,
)


class SubCategoryShortSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()
    class Meta:
        model = SubCategories
        fields = ["id", "name", "slug"]

    @extend_schema_field(str)
    def get_name(self, obj):
        language = self.context.get("language", "uk")
        return obj.safe_translation_getter(
            "name", language_code=language, default="Без назви"
        )

    @extend_schema_field(str)
    def get_slug(self, obj):
        language = self.context.get("language", "uk")
        return obj.safe_translation_getter("slug", language_code=language, default=None)


class CategoriesTreeSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()
    subcategories = SubCategoryShortSerializer(many=True, read_only=True)

    class Meta:
        model = Categories
        fields = [
            "id",
            "name",
            "slug",
            "updated_at",
            "has_length",
            "has_width",
            "has_diameter",
            "has_weight",
            "subcategories",
        ]

    @extend_schema_field(str)
    def get_name(self, obj):
        language = self.context.get("language", "uk")
        return obj.safe_translation_getter(
            "name", language_code=language, default="Без назви"
        )

    @extend_schema_field(str)
    def get_slug(self, obj):
        language = self.context.get("language", "uk")
        return obj.safe_translation_getter("slug", language_code=language, default=None)


class CategoriesSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()

    class Meta:
        model = Categories
        fields = [
            "id",
            "name",
            "slug",
            "updated_at",
            "has_length",
            "has_width",
            "has_diameter",
            "has_weight",
        ]

    @extend_schema_field(str)
    def get_name(self, obj):
        language = self.context.get("language", "uk")
        return obj.safe_translation_getter(
            "name", language_code=language, default="Без назви"
        )

    @extend_schema_field(str)
    def get_slug(self, obj):
        language = self.context.get("language", "uk")
        return obj.safe_translation_getter("slug", language_code=language, default=None)


class DescriptionsSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()
    text = serializers.SerializerMethodField()
    seo_title = serializers.SerializerMethodField()
    seo_description = serializers.SerializerMethodField()
    keywords = serializers.SerializerMethodField()

    class Meta:
        model = Descriptions
        fields = [
            "id",
            "name",
            "slug",
            "text",
            "seo_title",
            "seo_description",
            "keywords",
        ]

    @extend_schema_field(str)
    def get_slug(self, obj):
        return obj.safe_translation_getter("slug", default=None)

    @extend_schema_field(str)
    def get_name(self, obj):
        return obj.safe_translation_getter("name", default="Без назви")

    @extend_schema_field(str)
    def get_text(self, obj):
        return obj.safe_translation_getter("text", default="Без назви")

    @extend_schema_field(str)
    def get_seo_title(self, obj):
        return obj.safe_translation_getter("seo_title", default="Без назви")

    @extend_schema_field(str)
    def get_seo_description(self, obj):
        return obj.safe_translation_getter("seo_description", default="Без назви")

    @extend_schema_field(str)
    def get_keywords(self, obj):
        return obj.safe_translation_getter("keywords", default="Без назви")


class MaterialSerializer(serializers.ModelSerializer):
    material = serializers.CharField(source="material_name")
    color = serializers.CharField(source="color_name")

    class Meta:
        model = Material
        fields = ["id", "material", "assay", "color", "article"]

    # class MaterialSerializer(serializers.ModelSerializer):
    #     name = serializers.SerializerMethodField()

    #     class Meta:
    #         model = Material
    #         fields = ["material", "assay", "color", "slug", "name"]

    @extend_schema_field(str)
    def get_name(self, obj):
        return f"{obj.get_material_display()} {obj.assay} {obj.get_color_display()}"


# class ProductGemstoneSerializer(serializers.ModelSerializer):
#     name = serializers.SerializerMethodField()

#     class Meta:
#         model = ProductGemstone
#         fields = ["id", "name", "slug"]

#     @extend_schema_field(str)
#     def get_name(self, obj):
#         language = self.context.get("language", "uk")
#         return obj.safe_translation_getter(
#             "name", language_code=language, default="Без назви"
        # )


class ProductGemstoneSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    gemstone = serializers.SerializerMethodField()
    color = serializers.SerializerMethodField()

    class Meta:
        model = ProductGemstone
        fields = ["id", "status_display", "gemstone", "color"]

    @extend_schema_field(str)
    def get_gemstone(self, obj):
        language = self.context.get("language", "uk")
        return (
            obj.gemstone.safe_translation_getter(
                "name", language_code=language, default="Без назви"
            )
            if obj.gemstone
            else None
        )

    @extend_schema_field(str)
    def get_color(self, obj):
        language = self.context.get("language", "uk")
        return (
            obj.color.safe_translation_getter(
                "name", language_code=language, default="Без кольору"
            )
            if obj.color
            else None
        )


# class ProductGemstoneSerializer(serializers.ModelSerializer):
#     status_display = serializers.CharField(source="get_status_display", read_only=True)
#     gemstone = serializers.CharField(source="gemstone.name", read_only=True)
#     color = serializers.CharField(source="color.name", read_only=True)

#     class Meta:
#         model = ProductGemstone
#         fields = ["id", "status_display", "gemstone", "color"]


class ProductMaterialSerializer(serializers.ModelSerializer):
    material = serializers.SerializerMethodField()

    class Meta:
        model = ProductMaterial
        fields = ["id", "is_primary", "set_included", "material"]

    @extend_schema_field(str)
    def get_material(self, obj):
        if not obj.material:
            return None

        material_obj = obj.material

        return {
            "material": material_obj.get_material_display(),  # "Золото"
            "assay": material_obj.assay,  # "585"
            "color": material_obj.get_color_display(),  # "Червоний"
            "slug": material_obj.safe_translation_getter("slug", default=None),
            "label": f"{material_obj.get_material_display()} {material_obj.assay} {material_obj.get_color_display()}",
        }


class ProductStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductStatus
        fields = ["id", "name", "slug"]


class ProductAttributesSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    # parent_product = serializers.CharField(source='parent_product.name', read_only=True)
    clasp_type = serializers.SerializerMethodField()
    coating_material = serializers.SerializerMethodField()
    weaving_type = serializers.SerializerMethodField()

    class Meta:
        model = ProductAttributes
        fields = [
            "id",
            "status_display",
            "gender",
            "weaving_type",
            "clasp_type",
            "coating_material",
        ]

    @extend_schema_field(str)
    def get_weaving_type(self, obj):
        return (
            obj.weaving_type.safe_translation_getter("name", default="Без назви")
            if obj.weaving_type
            else None
        )

    @extend_schema_field(str)
    def get_clasp_type(self, obj):
        return (
            obj.clasp_type.safe_translation_getter("name", default="Без назви")
            if obj.clasp_type
            else None
        )

    @extend_schema_field(str)
    def get_coating_material(self, obj):
        return (
            obj.coating_material.safe_translation_getter("name", default="Без назви")
            if obj.coating_material
            else None
        )


class SubProductsSizesSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    old_price = serializers.SerializerMethodField()
    discount_applied = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    new_price = serializers.SerializerMethodField()

    def get_size(self, obj):
        if obj.size:
            if isinstance(obj.size, dict) and "value" in obj.size:
                return obj.size["value"]
            return str(obj.size)
        if obj.length and obj.max_length:
            return f"{obj.length}-{obj.max_length}"
        if obj.length:
            return str(obj.length)
        return ""

    def get_new_price(self, obj):
        # Перевіряємо, чи discount_percentage не None і більше 0
        if obj.discount_percentage is not None and obj.discount_percentage > 0:
            request = self.context.get("request")
            user = request.user if request and hasattr(request, "user") else None
            return get_discounted_price(user, obj)["new_price"]
        return None

    def get_old_price(self, obj):
        # Перевіряємо, чи discount_percentage не None і більше 0
        if obj.discount_percentage is not None and obj.discount_percentage > 0:
            request = self.context.get("request")
            user = request.user if request and hasattr(request, "user") else None
            return get_discounted_price(user, obj)["old_price"]
        return None

    def get_discount_applied(self, obj):
        # Повертаємо True, якщо є знижка (не None і більше 0)
        return obj.discount_percentage is not None and obj.discount_percentage > 0

    class Meta:
        model = SubProducts
        fields = [
            "id",
            "position",
            "ean_13",
            "sku",
            "article",
            "weight",
            "price",
            "discount_percentage",
            "new_price",
            "old_price",
            "discount_applied",
            "status_display",
            "size",
            "length",
            "max_length",
            "width",
        ]


class SubCategoriesSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()
    # parent = CategoriesSerializer()

    class Meta:
        model = SubCategories
        fields = ["id", "name", "slug", "parent"]

    @extend_schema_field(str)
    def get_name(self, obj):
        return obj.safe_translation_getter("name", default="Без назви")

    @extend_schema_field(str)
    def get_slug(self, obj):
        return obj.safe_translation_getter("slug", default=None)


class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ["id", "image", "uploaded_at"]

    def get_image(self, obj):
        if obj.image:
            # Примусово формуємо правильний URL
            public_id = str(obj.image)  # Отримуємо public_id (msadf0szr5dhc7ght0cc)
            return f"{CLOUDINARY_IMAGE_FIXED_PREFIX_PATH}{public_id}.png"
        return None


class ProductCertificateSerializer(serializers.ModelSerializer):
    file = serializers.SerializerMethodField()

    class Meta:
        model = ProductCertificate
        fields = ["id", "file", "uploaded_at"]

    def get_file(self, obj):
        if obj.file:
            # Примусово формуємо правильний URL
            public_id = str(obj.file)  # Отримуємо public_id (msadf0szr5dhc7ght0cc)
            return f"{CLOUDINARY_FILE_FIXED_PREFIX_PATH}{public_id}.png"
        return None


class ProductSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    certificates = serializers.SerializerMethodField()
    statuses = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    subcategory = SubCategoriesSerializer(read_only=True)
    subproducts = SubProductsSizesSerializer(many=True, read_only=True)
    gemstone = serializers.SerializerMethodField()
    materials = ProductMaterialSerializer(many=True, read_only=True)
    attributes = ProductAttributesSerializer(many=True, read_only=True)
    design = serializers.SerializerMethodField()
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    name = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()
    collection = serializers.SerializerMethodField()
    occasions = serializers.SerializerMethodField()
    description = DescriptionsSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "category",
            "subcategory",
            "name",
            "slug",
            "ean_13",
            "sku",
            "article",
            "collection",
            "statuses",
            "year_collection",
            "occasions",
            "design",
            "status_display",
            "subproducts",
            "gemstone",
            "materials",
            "attributes",
            "images",
            "certificates",
            "description",
        ]

    @extend_schema_field(List[str])
    def get_occasions(self, obj):
        language = self.context.get("language", "uk")
        return [
            occasion.safe_translation_getter(
                "name", language_code=language, default="Без назви"
            )
            for occasion in obj.occasions.all()
        ]
    @extend_schema_field(serializers.ListField(child=serializers.DictField()))
    def get_gemstone(self, obj):
        language = self.context.get('language', 'uk')
        gemstones = obj.gemstones.all()
        return ProductGemstoneSerializer(gemstones, many=True, context={'language': language}).data if gemstones else None
    # @extend_schema_field(serializers.ListField(child=serializers.DictField()))
    # def get_gemstone(self, obj):
    #     language = self.context.get("language", "uk")
    #     gemstones = obj.gemstones.all()
    #     return (
    #         ProductGemstoneSerializer(
    #             gemstones, many=True, context={"language": language}
    #         ).data
    #         if gemstones
    #         else None
    #     )

    @extend_schema_field(str)
    def get_category(self, obj):
        language = self.context.get("language", "uk")
        return (
            obj.category.safe_translation_getter(
                "name", language_code=language, default="Без категорії"
            )
            if obj.category
            else None
        )

    @extend_schema_field(str)
    def get_name(self, obj):
        language = self.context.get("language", "uk")
        return obj.safe_translation_getter(
            "name", language_code=language, default="Без назви"
        )

    @extend_schema_field(str)
    def get_collection(self, obj):
        language = self.context.get("language", "uk")
        return (
            obj.collection.safe_translation_getter(
                "name", language_code=language, default="Без колекції"
            )
            if obj.collection
            else None
        )

    @extend_schema_field(str)
    def get_design(self, obj):
        language = self.context.get("language", "uk")
        return (
            obj.design.safe_translation_getter(
                "name", language_code=language, default="Без дизайну"
            )
            if obj.design
            else None
        )

    @extend_schema_field(str)
    def get_slug(self, obj):
        language = self.context.get("language", "uk")
        return obj.safe_translation_getter("slug", language_code=language, default=None)

    @extend_schema_field(List[str])
    def get_statuses(self, obj):
        language = self.context.get("language", "uk")
        return [
            status.safe_translation_getter("name", language_code=language, default=None)
            for status in obj.statuses.all()
        ]

    @extend_schema_field(List[str])
    def get_images(self, obj):
        request = self.context.get("request")
        return [str(img.image) for img in obj.images.all()] if request else []

    @extend_schema_field(List[str])
    def get_certificates(self, obj):
        request = self.context.get("request")
        return [str(cert.file) for cert in obj.certificates.all()] if request else []


# class ProductSerializer(serializers.ModelSerializer):
#     images = serializers.SerializerMethodField()
#     certificates = serializers.SerializerMethodField()
#     statuses = serializers.SerializerMethodField()
#     category = serializers.SerializerMethodField()
#     subcategory = SubCategoriesSerializer(read_only=True)
#     subproducts = SubProductsSizesSerializer(many=True, read_only=True)
#     gemstone = serializers.SerializerMethodField()
#     materials = ProductMaterialSerializer(many=True, read_only=True)
#     attributes = ProductAttributesSerializer(many=True, read_only=True)
#     design = serializers.SerializerMethodField()
#     status_display = serializers.CharField(source="get_status_display", read_only=True)
#     name = serializers.SerializerMethodField()
#     slug = serializers.SerializerMethodField()
#     collection = serializers.SerializerMethodField()
#     occasions = serializers.SerializerMethodField()
#     description = DescriptionsSerializer(many=True, read_only=True)

#     class Meta:
#         model = Product
#         fields = [
#             "id",
#             "category",
#             "subcategory",
#             "name",
#             "slug",
#             "ean_13",
#             "sku",
#             "article",
#             "collection",
#             "statuses",
#             "year_collection",
#             "occasions",
#             "design",
#             "status_display",
#             "subproducts",
#             "gemstone",
#             "materials",
#             "attributes",
#             "images",
#             "certificates",
#             "description",
#         ]

#     @extend_schema_field(str)
#     def get_occasions(self, obj):
#         return (
#             obj.safe_translation_getter("name", default="Без назви")
#             if obj.occasions
#             else None
#         )

#     @extend_schema_field(str)
#     def get_gemstone(self, obj):
#         gemstones = obj.gemstones.all()  # Використовуємо related_name="gemstones"
#         return (
#             ProductGemstoneSerializer(gemstones, many=True).data if gemstones else None
#         )

#     @extend_schema_field(str)
#     def get_category(self, obj):
#         return (
#             obj.category.safe_translation_getter("name", default="Без назви")
#             if obj.category
#             else None
#         )

#     @extend_schema_field(str)
#     def get_name(self, obj):
#         return obj.safe_translation_getter("name", default="Без назви")

#     @extend_schema_field(str)
#     def get_collection(self, obj):
#         return (
#             obj.safe_translation_getter("name", default="Без назви")
#             if obj.collection
#             else None
#         )

#     @extend_schema_field(str)
#     def get_design(self, obj):
#         return (
#             obj.safe_translation_getter("name", default="Без назви")
#             if obj.design
#             else None
#         )

#     @extend_schema_field(str)
#     def get_slug(self, obj):
#         return obj.safe_translation_getter("slug", default=None)

#     @extend_schema_field(str)
#     def get_statuses(self, obj):
#         return [
#             status.safe_translation_getter("name", default=None)
#             for status in obj.statuses.all()
#         ]

#     @extend_schema_field(List[str])  # Вказуємо, що повертається список рядків
#     def get_images(self, obj):
#         request = self.context.get("request")
#         return [str(img.image) for img in obj.images.all()] if request else []
#         # return [request.build_absolute_uri(img.image.url) for img in obj.images.all()] if request else [img.image.url for img in obj.images.all()]

#     @extend_schema_field(List[str])  # Вказуємо, що повертається список рядків
#     def get_certificates(self, obj):
#         request = self.context.get("request")
#         return [str(cert.file) for cert in obj.certificates.all()] if request else []


class RingSizeSerializer(serializers.Serializer):
    finger_circumference = serializers.FloatField(help_text="Обхват пальця в мм")
    ring_size = serializers.FloatField(help_text="Розмір кільця за стандартом")


class TotalProductsSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    certificates = serializers.SerializerMethodField()
    statuses = serializers.SerializerMethodField()
    category = CategoriesSerializer(read_only=True)
    subcategory = SubCategoriesSerializer(read_only=True)
    name = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()
    design = serializers.SerializerMethodField()
    subproducts = SubProductsSizesSerializer(many=True, read_only=True)
    attributes = ProductAttributesSerializer(many=True, read_only=True)
    gemstone = serializers.SerializerMethodField()
    material = serializers.SerializerMethodField()
    description = DescriptionsSerializer(many=True, read_only=True)
    occasions = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "category",
            "subcategory",
            "name",
            "slug",
            "ean_13",
            "sku",
            "article",
            "statuses",
            "collection",
            "occasions",
            "description",
            "subproducts",
            "gemstone",
            "material",
            "images",
            "certificates",
            "design",
            "attributes",
            "year_collection",
        ]

    @extend_schema_field(str)
    def get_occasions(self, obj):
        return (
            obj.safe_translation_getter("name", default="Без назви")
            if obj.occasions
            else None
        )

    @extend_schema_field(str)
    def get_gemstone(self, obj):
        gemstones = obj.gemstones.all()  # Використовуємо related_name="gemstones"
        return (
            ProductGemstoneSerializer(gemstones, many=True).data if gemstones else None
        )

    @extend_schema_field(str)
    def get_material(self, obj):
        materials = obj.materials.all()  # Використовуємо related_name="gemstones"
        return (
            ProductMaterialSerializer(materials, many=True).data if materials else None
        )

    @extend_schema_field(str)
    def get_design(self, obj):
        return (
            obj.safe_translation_getter("name", default="Без назви")
            if obj.design
            else None
        )

    @extend_schema_field(str)
    def get_name(self, obj):
        return obj.safe_translation_getter("name", default="Без назви")

    @extend_schema_field(str)
    def get_slug(self, obj):
        return obj.safe_translation_getter("slug", default=None)

    @extend_schema_field(str)
    def get_statuses(self, obj):
        return [
            status.safe_translation_getter("name", default=None)
            for status in obj.statuses.all()
        ]

    @extend_schema_field(str)
    def get_category(self, obj):
        return (
            obj.category.safe_translation_getter("name", default="Без назви")
            if obj.category
            else None
        )

    @extend_schema_field(List[str])  # Вказуємо, що повертається список рядків
    def get_images(self, obj):
        request = self.context.get("request")
        return [str(img.image) for img in obj.images.all()] if request else []
        # return (
        #     [request.build_absolute_uri(img.image.url) for img in obj.images.all()]
        #     if request
        #     else [img.image.url for img in obj.images.all()]
        # )

    @extend_schema_field(List[str])  # Вказуємо, що повертається список рядків
    def get_certificates(self, obj):
        request = self.context.get("request")
        return [str(cert.file) for cert in obj.certificates.all()] if request else []
