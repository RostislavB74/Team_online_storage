from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny,
)
from rest_framework import viewsets

from utils.language_code import get_language_code
from .models import (
    Product,
    Categories,
)
from .serializers import (
    ProductSerializer,
    CategoriesSerializer,
)
from django.shortcuts import get_object_or_404


class CategoriesViewSet(viewsets.ModelViewSet):
    """CRUD для продуктів"""

    # queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        """Фільтрація товарів за мовою"""
        lang = self.request.GET.get("lang", "uk")
        if lang == "uk":
            return Categories.objects.filter(translations__language_code="uk")
        return Categories.objects.filter(translations__language_code="en")

    def retrieve(self, request, *args, **kwargs):
        """Отримання продукту за slug з урахуванням мови"""
        lang = request.GET.get("lang", "uk")
        field = "translations__slug"  # Вказуємо, що шукаємо в перекладах
        result = get_object_or_404(
            Categories, **{field: kwargs["pk"], "translations__language_code": lang}
        )
        serializer = self.get_serializer(result)
        return Response(serializer.data)

    @extend_schema(
        summary="Get example data",
        description="Returns an example response with some data.",
        responses={200: dict},
    )
    def get(self, request):
        return Response({"message": "Hello, API!"})


class CategoriesAPIList(generics.ListCreateAPIView):
    """Отримати список продуктів або створити новий"""

    # queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        """Фільтрація за мовою"""
        lang = get_language_code(self.request)
        result = Categories.objects.language(lang).all()
        return result


class CategoriesAPIDetail(generics.RetrieveAPIView):
    """Отримати деталі продукту"""

    # queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        """Фільтрація за мовою"""
        lang = get_language_code(self.request)
        result = Categories.objects.language(lang).all()
        return result


class CategoriesAPIUpdate(generics.RetrieveUpdateAPIView):
    """Оновлення продукту"""

    queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer
    permission_classes = (AllowAny,)


class ProductViewSet(viewsets.ModelViewSet):
    """CRUD для продуктів"""

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        """Фільтрація товарів за мовою"""
        lang = get_language_code(self.request)
        return Product.objects.language(lang).all()

    def retrieve(self, request, *args, **kwargs):
        """Отримання продукту за slug з урахуванням мови"""
        lang = request.GET.get("lang", "uk")
        field = "translations__slug"  # Вказуємо, що шукаємо в перекладах
        product = get_object_or_404(
            Product, **{field: kwargs["pk"], "translations__language_code": lang}
        )
        serializer = self.get_serializer(product)
        return Response(serializer.data)

    @extend_schema(
        summary="Get example data",
        description="Returns an example response with some data.",
        responses={200: dict},
    )
    def get(self, request):
        return Response({"message": "Hello, API!"})


class ProductAPIList(generics.ListCreateAPIView):
    """Отримати список продуктів або створити новий"""

    # queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        """Фільтрація товарів за мовою"""
        lang = get_language_code(self.request)
        return Product.objects.language(lang).all()


class ProductAPIDetail(generics.RetrieveAPIView):
    """Отримати деталі продукту"""

    # queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        """Фільтрація товарів за мовою"""
        lang = get_language_code(self.request)
        return Product.objects.language(lang).all()


class ProductAPIUpdate(generics.RetrieveUpdateAPIView):
    """Оновлення продукту"""

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (IsAuthenticated,)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import F
from django.db.models.functions import Abs
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from .models import RingSizeConversion  # Імпортуйте свою модель
from .serializers import RingSizeSerializer  # Імпортуйте серіалізатор


class RingSizeLookup(APIView):
    """Переводить окружність пальця в розмір кільця, знаходячи найближче значення"""

    serializer_class = RingSizeSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="circumference",
                description="Окружність пальця в міліметрах (напр. 60)",
                required=True,
                type=OpenApiTypes.FLOAT,
                location=OpenApiParameter.QUERY,
            )
        ],
        responses={200: RingSizeSerializer},
    )
    def get(self, request, *args, **kwargs):
        circumference = request.query_params.get("circumference")

        if not circumference:
            return Response(
                {"error": "Circumference is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            circumference = float(circumference)

            # Шукаємо точний розмір
            size_obj = RingSizeConversion.objects.filter(
                circumference_mm=circumference
            ).first()
            if size_obj:
                return Response(self.serialize_size(size_obj))

            # Якщо точного значення немає, шукаємо найближчий розмір
            nearest_size = (
                RingSizeConversion.objects.annotate(
                    diff=Abs(F("circumference_mm") - circumference)
                )
                .order_by("diff")
                .first()
            )

            if nearest_size:
                return Response(self.serialize_size(nearest_size))
            else:
                return Response(
                    {"error": "No sizes available"}, status=status.HTTP_404_NOT_FOUND
                )

        except ValueError:
            return Response(
                {"error": "Invalid circumference value"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def serialize_size(self, size_obj):
        """Серіалізуємо відповідь для зручного відображення"""
        return {
            "circumference_mm": size_obj.circumference_mm,
            "size_ua": size_obj.size_ua,
            "size_us": size_obj.size_us,
            "size_eu": size_obj.size_eu,
            "size_uk": size_obj.size_uk,
            "size_asia": size_obj.size_asia,
            "size_other_eu": size_obj.size_other_eu,
        }


# class RingSizeLookup(APIView):
#     """Переводить окружність пальця в розмір кільця, знаходячи найближче значення"""
#     serializer_class = RingSizeSerializer
#     def get(self, request, *args, **kwargs):
#         circumference = request.query_params.get("circumference")

#         if not circumference:
#             return Response({"error": "Circumference is required"}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             circumference = float(circumference)

#             # Шукаємо точний розмір
#             size_obj = RingSizeConversion.objects.filter(circumference_mm=circumference).first()
#             if size_obj:
#                 return Response(self.serialize_size(size_obj))

#             # Якщо точного значення немає, шукаємо найближчий розмір
#             nearest_size = (
#                 RingSizeConversion.objects
#                 .annotate(diff=Abs(F("circumference_mm") - circumference))  # Абсолютна різниця
#                 .order_by("diff")  # Найменша різниця буде першою
#                 .first()
#             )

#             if nearest_size:
#                 return Response(self.serialize_size(nearest_size))
#             else:
#                 return Response({"error": "No sizes available"}, status=status.HTTP_404_NOT_FOUND)

#         except ValueError:
#             return Response({"error": "Invalid circumference value"}, status=status.HTTP_400_BAD_REQUEST)

#     def serialize_size(self, size_obj):
#         """Серіалізуємо відповідь для зручного відображення"""
#         return {
#             "circumference_mm": size_obj.circumference_mm,
#             "size_ua": size_obj.size_ua,
#             "size_us": size_obj.size_us,
#             "size_eu": size_obj.size_eu,
#             "size_uk": size_obj.size_uk,
#             "size_asia": size_obj.size_asia,
#             "size_other_eu": size_obj.size_other_eu,
#         }
# # class RingSizeLookup(APIView):
# #     """Переводить окружність пальця в розмір кільця"""
# #     def get(self, request, *args, **kwargs):
# #         circumference = request.query_params.get("circumference")
# #         if not circumference:
# #             return Response({"error": "Circumference is required"}, status=status.HTTP_400_BAD_REQUEST)

# #         try:
# #             circumference = float(circumference)
# #             size_obj = RingSizeConversion.objects.filter(circumference_mm=circumference).first()

# #             if size_obj:
# #                 return Response({
# #                     "circumference_mm": size_obj.circumference_mm,
# #                     "size_ua": size_obj.size_ua,
# #                     "size_us": size_obj.size_us,
# #                     "size_eu": size_obj.size_eu,
# #                     "size_uk": size_obj.size_uk,
# #                     "size_asia": size_obj.size_asia,
# #                     "size_other_eu": size_obj.size_other_eu,
# #                 })
# #             else:
# #                 return Response({"error": "Size not found"}, status=status.HTTP_404_NOT_FOUND)

# #         except ValueError:
# #             return Response({"error": "Invalid circumference value"}, status=status.HTTP_400_BAD_REQUEST)
