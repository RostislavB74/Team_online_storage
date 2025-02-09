from rest_framework import serializers
from .models import Product, ProductImage, ProductCertificate

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'uploaded_at']

class ProductCertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCertificate
        fields = ['id', 'file', 'uploaded_at']

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    certificates = ProductCertificateSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'images', 'certificates']
from .models import Product, RingSizeConversion

# class RingSizeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = RingSizeConversion
#         fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    size = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'

    def get_size(self, obj):
        if obj.category and obj.category.name.lower() == "каблучки" and obj.circumference_mm:
            size_obj = RingSizeConversion.objects.filter(
                circumference_mm=obj.circumference_mm
            ).first()
            return size_obj.size_ua if size_obj else None
        return None