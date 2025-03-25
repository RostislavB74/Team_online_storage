from rest_framework import serializers
from typing import List  # Для типу List[str]
from drf_spectacular.utils import extend_schema_field
from .models import *

class CategoriesSerializer(serializers.ModelSerializer):
    name=serializers.SerializerMethodField()
    slug=serializers.SerializerMethodField()
    class Meta:
        model = Categories
        fields = ['id', 'name', 'slug', 'updated_at']
    @extend_schema_field(str)
    def get_name(self, obj):
        return obj.safe_translation_getter('name', default='Без назви')

    @extend_schema_field(str)
    def get_slug(self, obj):
        return obj.safe_translation_getter('slug', default=None)


class ProductStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductStatus
        fields = ['id', 'name', 'slug']

class SubProductsSizesSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    parent_product = serializers.CharField(source='parent_product.name', read_only=True)

    class Meta:
        model = SubProducts
        fields = [
            'id','parent_product','position', 'ean_13', 'sku', 'article','weight' , 'price',  'status_display',
            'size','length','width'
        ]
    
class SubCategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategories
        fields = ['id', 'name', 'slug', 'category','uploaded_at']


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'uploaded_at']

class ProductCertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCertificate
        fields = ['id', 'file', 'uploaded_at']

class ProductSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    certificates = serializers.SerializerMethodField()
    statuses = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    subcategory = serializers.SerializerMethodField()
    subproducts = SubProductsSizesSerializer(many=True, read_only=True)
    design=serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    name=serializers.SerializerMethodField()
    slug=serializers.SerializerMethodField()
    collection=serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = [
            'id','category','subcategory', 'name', 'slug', 'ean_13', 'sku', 'article',  'collection', 'statuses','year_collection','occasions' , 'design', 'status_display','subproducts', 'images', 'certificates',
            
        ]
    @extend_schema_field(str)
    def get_category(self, obj):
        return obj.category.safe_translation_getter('name', default='Без назви') if obj.category else None

    @extend_schema_field(str)
    def get_subcategory(self, obj):
        return obj.subcategory.safe_translation_getter('name', default='Без назви') if obj.subcategory else None
    
    @extend_schema_field(str)
    def get_name(self, obj):
        return obj.safe_translation_getter('name', default='Без назви')
    @extend_schema_field(str)
    def get_collection(self, obj):
        return obj.safe_translation_getter('name', default='Без назви')if obj.collection else None
    @extend_schema_field(str)
    def get_design(self, obj):
        return obj.safe_translation_getter('name', default='Без назви')if obj.design else None

    @extend_schema_field(str)
    def get_slug(self, obj):
        return obj.safe_translation_getter('slug', default=None)
    @extend_schema_field(str)
    def get_statuses(self, obj):
        return obj.category.safe_translation_getter('name', default='Без назви') if obj.statuses else None
    @extend_schema_field(List[str])  # Вказуємо, що повертається список рядків
    def get_images(self, obj):
        request = self.context.get('request')
        return [request.build_absolute_uri(img.image.url) for img in obj.images.all()] if request else [img.image.url for img in obj.images.all()]

    @extend_schema_field(List[str])  # Вказуємо, що повертається список рядків
    def get_certificates(self, obj):
        request = self.context.get('request')
        return [request.build_absolute_uri(cert.file.url) for cert in obj.certificates.all()] if request else [cert.file.url for cert in obj.certificates.all()]
class RingSizeSerializer(serializers.Serializer):
    finger_circumference = serializers.FloatField(help_text="Обхват пальця в мм")
    ring_size = serializers.FloatField(help_text="Розмір кільця за стандартом")


from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import Product, Categories, SubCategories, ProductStatus

from rest_framework import serializers
from .models import Product, Categories, SubCategories, ProductStatus

class TotalProductsSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    certificates = serializers.SerializerMethodField()
    statuses = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    subcategory = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()
    subproducts = SubProductsSizesSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id", "category", "subcategory", "name", "slug", "ean_13", "sku", "article", "statuses",
            "collection", "occasions", "subproducts", "images", "certificates", "design",
        ]

    @extend_schema_field(str)
    def get_name(self, obj):
        return obj.safe_translation_getter('name', default='Без назви')

    @extend_schema_field(str)
    def get_slug(self, obj):
        return obj.safe_translation_getter('slug', default=None)
    @extend_schema_field(str)
    def get_statuses(self, obj):
        return obj.category.safe_translation_getter('name', default='Без назви') if obj.statuses else None

    @extend_schema_field(str)
    def get_category(self, obj):
        return obj.category.safe_translation_getter('name', default='Без назви') if obj.category else None

    @extend_schema_field(str)
    def get_subcategory(self, obj):
        return obj.subcategory.safe_translation_getter('name', default='Без назви') if obj.subcategory else None

    @extend_schema_field(List[str])  # Вказуємо, що повертається список рядків
    def get_images(self, obj):
        request = self.context.get('request')
        return [request.build_absolute_uri(img.image.url) for img in obj.images.all()] if request else [img.image.url for img in obj.images.all()]

    @extend_schema_field(List[str])  # Вказуємо, що повертається список рядків
    def get_certificates(self, obj):
        request = self.context.get('request')
        return [request.build_absolute_uri(cert.file.url) for cert in obj.certificates.all()] if request else [cert.file.url for cert in obj.certificates.all()]
# class TotalProductsSerializer(serializers.ModelSerializer):
#     images = serializers.SerializerMethodField()
#     certificates = serializers.SerializerMethodField()
#     statuses = serializers.SlugRelatedField(
#         many=True, queryset=ProductStatus.objects.all(), slug_field="name"
#     )
#     category = serializers.SerializerMethodField()
#     subcategory = serializers.SerializerMethodField()
#     subproducts = SubProductsSizesSerializer(many=True, read_only=True)

#     class Meta:
#         model = Product
#         fields = [
#             "id", "category", "subcategory", "name", "slug", "ean_13", "sku", "article", "statuses",
#             "collection", "occasions", "subproducts", "images", "certificates"
#         ]

#     def to_representation(self, instance):
#         representation = super().to_representation(instance)
#         # Обробка перекладених полів моделі Product
#         representation['name'] = instance.safe_translation_getter('name', default='Без назви')
#         representation['slug'] = instance.safe_translation_getter('slug', default=None)
#         # Обробка перекладених полів пов’язаних моделей
#         representation['category'] = (
#             instance.category.safe_translation_getter('name', default='Без назви')
#             if instance.category
#             else None
#         )
#         representation['subcategory'] = (
#             instance.subcategory.safe_translation_getter('name', default='Без назви')
#             if instance.subcategory
#             else None
#         )
#         return representation

#     def get_images(self, obj):
#         request = self.context.get('request')
#         return [request.build_absolute_uri(img.image.url) for img in obj.images.all()] if request else [img.image.url for img in obj.images.all()]

#     def get_certificates(self, obj):
#         request = self.context.get('request')
#         return [request.build_absolute_uri(cert.file.url) for cert in obj.certificates.all()] if request else [cert.file.url for cert in obj.certificates.all()]

#     # Додаємо методи для category і subcategory, щоб уникнути конфліктів із Meta.fields
#     @extend_schema_field(str)
#     def get_category(self, obj):
#         return obj.category.safe_translation_getter('name', default='Без назви') if obj.category else None

#     @extend_schema_field(str)
#     def get_subcategory(self, obj):
#         return obj.subcategory.safe_translation_getter('name', default='Без назви') if obj.subcategory else None
# class TotalProductsSerializer(serializers.ModelSerializer):
#     images = serializers.SerializerMethodField()
#     certificates = serializers.SerializerMethodField()
#     statuses = serializers.SlugRelatedField(
#         many=True, queryset=ProductStatus.objects.all(), slug_field="name"
#     )
#     category = serializers.SerializerMethodField()
#     subcategory = serializers.SerializerMethodField()
#     name = serializers.SlugRelatedField(many=False, queryset=Product.objects.all(), slug_field="name_property")  # Додаємо для name
#     slug = serializers.SlugRelatedField(many=False, queryset=Product.objects.all(), slug_field="slug_property")
#     subproducts = SubProductsSizesSerializer(many=True, read_only=True)

#     class Meta:
#         model = Product
#         fields = [
#             "id", "category", "subcategory", "name", "slug", "ean_13", "sku", "article", "statuses",
#             "collection", "occasions", "subproducts", "images", "certificates"
#         ]

#     @extend_schema_field(str)
#     def get_name(self, obj):
#         return obj.safe_translation_getter('name', default='Без назви')

#     @extend_schema_field(str)
#     def get_slug(self, obj):
#         return obj.safe_translation_getter('slug', default=None)

#     @extend_schema_field(str)
#     def get_category(self, obj):
#         return obj.category.safe_translation_getter('name', default='Без назви') if obj.category else None

#     @extend_schema_field(str)
#     def get_subcategory(self, obj):
#         return obj.subcategory.safe_translation_getter('name', default='Без назви') if obj.subcategory else None

#     def get_images(self, obj):
#         request = self.context.get('request')
#         return [request.build_absolute_uri(img.image.url) for img in obj.images.all()] if request else [img.image.url for img in obj.images.all()]

#     def get_certificates(self, obj):
#         request = self.context.get('request')
#         return [request.build_absolute_uri(cert.file.url) for cert in obj.certificates.all()] if request else [cert.file.url for cert in obj.certificates.all()]