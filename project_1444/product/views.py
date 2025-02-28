from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets
from .models import Product, ProductImage, ProductCertificate, RingSizeConversion
from .serializers import ProductSerializer, ProductImageSerializer, ProductCertificateSerializer

class ProductViewSet(viewsets.ModelViewSet):
    """CRUD для продуктів"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )

class ProductAPIList(generics.ListCreateAPIView):
    """Отримати список продуктів або створити новий"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )


class ProductAPIDetail(generics.RetrieveAPIView):
    """Отримати деталі продукту"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )


class ProductAPIUpdate(generics.RetrieveUpdateAPIView):
    """Оновлення продукту"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (IsAuthenticated, )


class RingSizeLookup(APIView):
    """Переводить окружність пальця в розмір кільця"""
    def get(self, request, *args, **kwargs):
        circumference = request.query_params.get("circumference")
        if not circumference:
            return Response({"error": "Circumference is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            circumference = float(circumference)
            size_obj = RingSizeConversion.objects.filter(circumference_mm=circumference).first()

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

