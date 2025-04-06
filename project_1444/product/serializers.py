from rest_framework import serializers
from typing import List  # Для типу List[str]
from drf_spectacular.utils import extend_schema_field
from .models import *

class ProductGemstoneSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    gemstone = serializers.CharField(source='gemstone.name', read_only=True)
    color = serializers.CharField(source='color.name', read_only=True)

    class Meta:
        model = ProductGemstone
        fields = ['id', 'status_display', 'gemstone', 'color']
class ProductMaterialSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    material = serializers.CharField(source='material.name', read_only=True)

    class Meta:
        model = ProductMaterial
        fields = ['id', 'status_display', 'material']

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
class DescriptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Descriptions
        fields = ['id', 'name', 'slug', 'text', 'seo_title', 'seo_description', 'keywords']
    @extend_schema_field(str)
    def get_slug(self, obj):
        return obj.safe_translation_getter('slug', default=None)
    @extend_schema_field(str)
    def get_name(self, obj):
        return obj.safe_translation_getter('name', default='Без назви')

class ProductStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductStatus
        fields = ['id', 'name', 'slug']

class ProductAttributesSerializer(serializers.ModelSerializer):
    status_display=serializers.CharField(source='get_status_display', read_only=True)
    # parent_product = serializers.CharField(source='parent_product.name', read_only=True)
    clasp_type=serializers.SerializerMethodField()
    coating_material=serializers.SerializerMethodField()
    weaving_type=serializers.SerializerMethodField()
    class Meta:
        model=ProductAttributes
        fields=['id','status_display', 'gender', 'weaving_type', 'clasp_type','coating_material', ]

    @extend_schema_field(str)
    def get_weaving_type(self, obj):
        return obj.weaving_type.safe_translation_getter('name', default='Без назви') if obj.weaving_type else None
    @extend_schema_field(str)
    def get_clasp_type(self, obj):
        return obj.clasp_type.safe_translation_getter('name', default='Без назви') if obj.clasp_type else None
    @extend_schema_field(str)
    def get_coating_material(self, obj):
        return obj.coating_material.safe_translation_getter('name', default='Без назви') if obj.coating_material else None
    # @extend_schema_field(str)
    # def get_description_coating(self, obj):
    #     return obj.description_coating.safe_translation_getter('name', default='Без назви') if obj.description_coating else None

class SubProductsSizesSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    # parent_product = serializers.CharField(source='parent_product.name', read_only=True)
    

    class Meta:
        model = SubProducts
        fields = [
            'id','position', 'ean_13', 'sku', 'article','weight' , 'price','discount_percentage', 'new_price', 'old_price' , 'status_display',
            'size','length','max_length' ,'width'
        ]
    
class SubCategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategories
        fields = ['id', 'name', 'slug', 'category','uploaded_at']

class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ["id", "image", "uploaded_at"]

    def get_image(self, obj):
        if obj.image:
            # Примусово формуємо правильний URL
            public_id = str(obj.image)  # Отримуємо public_id (msadf0szr5dhc7ght0cc)
            return f"https://res.cloudinary.com/dtftiyeso/image/upload/{public_id}.png"
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
            return f"https://res.cloudinary.com/dtftiyeso/file/upload/{public_id}.png"
        return None

class ProductSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    certificates = serializers.SerializerMethodField()
    statuses = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    subcategory = serializers.SerializerMethodField()
    subproducts = SubProductsSizesSerializer(many=True, read_only=True)
    gemstone = serializers.SerializerMethodField()
    materials = ProductMaterialSerializer(many=True, read_only=True)
    attributes = ProductAttributesSerializer(many=True, read_only=True)
    design = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    name = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()
    collection = serializers.SerializerMethodField()
    occasions=serializers.SerializerMethodField()
    description = DescriptionsSerializer(many=True, read_only=True)


    class Meta:
        model = Product
        fields = [
            'id', 'category', 'subcategory', 'name', 'slug', 'ean_13', 'sku', 
            'article', 'collection', 'statuses', 'year_collection', 'occasions', 
            'design', 'status_display', 'subproducts', 'gemstone', 'materials', 'attributes', 'images', 'certificates','description',
        ]
    
    @extend_schema_field(str)
    def get_occasions(self, obj):
       return obj.safe_translation_getter('name', default='Без назви')if obj.occasions else None
        
    @extend_schema_field(str)
    def get_gemstone(self, obj):
        gemstones = obj.gemstones.all()  # Використовуємо related_name="gemstones"
        return ProductGemstoneSerializer(gemstones, many=True).data if gemstones else None
        
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
        return [status.safe_translation_getter("name", default=None) for status in obj.statuses.all()]
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

class TotalProductsSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    certificates = serializers.SerializerMethodField()
    statuses = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    subcategory = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()
    design=serializers.SerializerMethodField()
    subproducts = SubProductsSizesSerializer(many=True, read_only=True)
    attributes=ProductAttributesSerializer(many=True, read_only=True)
    gemstone = serializers.SerializerMethodField()
    material = serializers.SerializerMethodField()
    description = DescriptionsSerializer(many=True, read_only=True)
    occasions = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = [
            "id", "category", "subcategory", "name", "slug", "ean_13", "sku", "article", "statuses",
            "collection", "occasions", "description","subproducts", "gemstone","material","images", "certificates", "design", 'attributes',
        ]
    @extend_schema_field(str)
    def get_occasions(self, obj):
       return obj.safe_translation_getter('name', default='Без назви')if obj.occasions else None
    
    @extend_schema_field(str)
    def get_gemstone(self, obj):
        gemstones = obj.gemstones.all()  # Використовуємо related_name="gemstones"
        return ProductGemstoneSerializer(gemstones, many=True).data if gemstones else None
    @extend_schema_field(str)
    def get_material(self, obj):
        materials = obj.materials.all()  # Використовуємо related_name="gemstones"
        return ProductMaterialSerializer(materials, many=True).data if materials else None
    
    @extend_schema_field(str)
    def get_design(self, obj):
        return obj.safe_translation_getter('name', default='Без назви')if obj.design else None
    @extend_schema_field(str)
    def get_name(self, obj):
        return obj.safe_translation_getter('name', default='Без назви')

    @extend_schema_field(str)
    def get_slug(self, obj):
        return obj.safe_translation_getter('slug', default=None)
    @extend_schema_field(str)
    def get_statuses(self, obj):
        return [status.safe_translation_getter("name", default=None) for status in obj.statuses.all()]
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
