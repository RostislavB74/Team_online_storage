from rest_framework import viewsets
from .models import Product, ProductImage, ProductCertificate
from .serializers import ProductSerializer, ProductImageSerializer, ProductCertificateSerializer, RingSizeSerializer

# class ProductViewSet(viewsets.ModelViewSet):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer

# class ProductImageViewSet(viewsets.ModelViewSet):
#     queryset = ProductImage.objects.all()
#     serializer_class = ProductImageSerializer

# class ProductCertificateViewSet(viewsets.ModelViewSet):
#     queryset = ProductCertificate.objects.all()
#     serializer_class = ProductCertificateSerializer
class RingSizeViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = RingSizeSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return RingSizeSerializer
        return super().get_serializer_class()