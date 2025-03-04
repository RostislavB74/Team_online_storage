from rest_framework import serializers
from .models import *

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
            'id', 'name',  'status', 'status_display', 'circumference_mm',
            'size', 'images', 'certificates'
        ]

    def get_size(self, obj):
        if obj.category and obj.category.name.lower() == "каблучки" and obj.circumference_mm:
            size_obj = RingSizeConversion.objects.filter(
                circumference_mm=obj.circumference_mm
            ).first()
            return size_obj.size_ua if size_obj else None
        return None



