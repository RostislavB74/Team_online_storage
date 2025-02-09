from rest_framework import viewsets
from .models import Product, ProductImage, ProductCertificate
from .serializers import ProductSerializer, ProductImageSerializer, ProductCertificateSerializer
from rest_framework.viewsets import ModelViewSet
from .models import Product
from rest_framework import serializers
from .serializers import ProductSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import RingSizeConversion
class ProductSerializer(serializers.ModelSerializer):
    product_images = ProductImageSerializer(many=True, read_only=True)
    product_certificates = ProductCertificateSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = '__all__'


class RingSizeLookup(APIView):
    def get(self, request, *args, **kwargs):
        circumference = request.query_params.get("circumference")
        if not circumference:
            return Response({"error": "Circumference is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            circumference = float(circumference)
            size_obj = RingSizeConversion.objects.filter(
                circumference_mm=circumference
            ).first()

            if size_obj:
                return Response({
                    "circumference_mm": size_obj.circumference_mm,
                    "size_ua": size_obj.size_ua,
                    "size_us": size_obj.size_us,
                    "size_eu": size_obj.size_eu,
                    "size_uk": size_obj.size_uk,
                    "size_asia": size_obj.size_asia,
                    "size_other_eu": size_obj.size_other_eu,
                })
            else:
                return Response({"error": "Size not found"}, status=status.HTTP_404_NOT_FOUND)

        except ValueError:
            return Response({"error": "Invalid circumference value"}, status=status.HTTP_400_BAD_REQUEST)
