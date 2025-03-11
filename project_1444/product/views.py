from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets
from .models import Product, ProductImage, ProductCertificate, RingSizeConversion, SubCategories, Categories
from .serializers import ProductSerializer, ProductImageSerializer, ProductCertificateSerializer, SubCategoriesSerializer, CategoriesSerializer
from django.shortcuts import get_object_or_404


class ProductViewSet(viewsets.ModelViewSet):
    """CRUD для продуктів"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, AllowAny)

    def get_queryset(self):
        """Фільтрація товарів за мовою"""
        lang = self.request.GET.get("lang", "uk")
        if lang == "uk":
            return Product.objects.filter(translations__language_code="uk")
        return Product.objects.filter(translations__language_code="en")

    def retrieve(self, request, *args, **kwargs):
        """Отримання продукту за slug з урахуванням мови"""
        lang = request.GET.get("lang", "uk")
        field = "translations__slug"  # Вказуємо, що шукаємо в перекладах
        product = get_object_or_404(Product, **{field: kwargs["pk"], "translations__language_code": lang})
        serializer = self.get_serializer(product)
        return Response(serializer.data)

class ProductAPIList(generics.ListCreateAPIView):
    """Отримати список продуктів або створити новий"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, AllowAny,)


class ProductAPIDetail(generics.RetrieveAPIView):
    """Отримати деталі продукту"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, AllowAny,)


class ProductAPIUpdate(generics.RetrieveUpdateAPIView):
    """Оновлення продукту"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (IsAuthenticated, )
class CategoriesViewSet(viewsets.ModelViewSet):
    """CRUD для продуктів"""
    queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, AllowAny,)

    def get_queryset(self):
        """Фільтрація категорій за мовою"""
        lang = self.request.GET.get("lang", "uk")
        if lang == "uk":
            return Categories.objects.filter(translations__language_code="uk")
        return Categories.objects.filter(translations__language_code="en")

    def retrieve(self, request, *args, **kwargs):
        """Отримання категорії за slug з урахуванням мови"""
        lang = request.GET.get("lang", "uk")
        field = "translations__slug"  # Вказуємо, що шукаємо в перекладах
        result = get_object_or_404(Categories, **{field: kwargs["pk"], "translations__language_code": lang})
        serializer = self.get_serializer(result)
        return Response(serializer.data)
    
class CategoriesAPIList(generics.ListCreateAPIView):
    queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer
    permission_classes=(IsAuthenticatedOrReadOnly,  AllowAny,)


class CategoriesAPIDetail(generics.RetrieveAPIView):
    """Отримати деталі продукту"""
    queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, AllowAny,)


class CategoriesAPIUpdate(generics.RetrieveUpdateAPIView):
    """Оновлення продукту"""
    queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer
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

