from rest_framework import serializers
from .models import *

class CategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = ['id', 'name', 'slug']

class SubCategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = ['id', 'name', 'slug']
class SubCategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategories
        fields = ['id', 'name', 'slug']


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'uploaded_at']

class ProductCertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCertificate
        fields = ['id', 'file', 'uploaded_at']

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, required=False)
    certificates = ProductCertificateSerializer(many=True, required=False)
    size = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id','category','subcategory', 'name', 'slug', 'ean_13', 'sku', 'article',  'price', 'collection', 'occasions' , 'status_display', 'circumference_mm',
            'size', 'images', 'certificates'
        ]

    def get_size(self, obj):
        if obj.category and obj.category.name.lower() == "каблучки" and obj.circumference_mm:
            size_obj = RingSizeConversion.objects.filter(
                circumference_mm=obj.circumference_mm
            ).first()
            return size_obj.size_ua if size_obj else None
      

class RingSizeSerializer(serializers.Serializer):
    finger_circumference = serializers.FloatField(help_text="Обхват пальця в мм")
    ring_size = serializers.FloatField(help_text="Розмір кільця за стандартом")