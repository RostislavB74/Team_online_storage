import django_filters
from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework import viewsets
from django.db.models import F, FloatField
from django.db.models.functions import Abs
from django.http import HttpResponse
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
    extend_schema_view,
)
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    IsAuthenticated,
    AllowAny,
)
from django.db.models import Prefetch
from utils.language_code import get_language_code
from utils.cache_headers import MixinCacheHeaders
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from .models import (
    Product,
    ProductImage,
    ProductCertificate,
    RingSizeConversion,
    Categories,
    SubProducts,
    Descriptions,
    SubCategories,
)
from .serializers import (
    ProductSerializer,
    CategoriesSerializer,
    ProductImageSerializer,
    ProductCertificateSerializer,
    CategoriesSerializer,
    RingSizeSerializer,
    SubProductsSizesSerializer,
    DescriptionsSerializer,
    TotalProductsSerializer,
    SubCategoriesSerializer,
)


@extend_schema(tags=["SubCategory API"])
class SubCategoriesAPIList(MixinCacheHeaders, generics.ListCreateAPIView):
    """Отримати список продуктів або створити новий"""

    # queryset = Categories.objects.all()
    serializer_class = SubCategoriesSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):  # noqa
        """Фільтрація за мовою"""
        lang = get_language_code(self.request)
        result = SubCategories.objects.language(lang).all()
        return result


@extend_schema_view(
    get=extend_schema(
        parameters=[
            OpenApiParameter(
                name="Accept-Language",
                description=_(
                    "Preferred language for the response. Allowed values: {languages_list}."
                ).format(languages_list=", ".join(settings.PARLER_LANGUAGES_LIST)),
                required=False,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.HEADER,
            )
        ],
    ),
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name="Accept-Language",
                description=_(
                    "Preferred language for the response. Allowed values: {languages_list}."
                ).format(languages_list=", ".join(settings.PARLER_LANGUAGES_LIST)),
                required=False,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.HEADER,
            )
        ],
    ),
)
@extend_schema(tags=["Category API"])
class CategoriesAPIList(MixinCacheHeaders, generics.ListCreateAPIView):
    """Отримати список продуктів або створити новий"""

    # queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        """Фільтрація за мовою"""
        lang = get_language_code(self.request)
        result = Categories.objects.language(lang).all()
        return result

    def get(self, request, *args, **kwargs):
        # Перевірка на наявність кешування
        cache_data = self.check_cache_headers(request)
        if isinstance(cache_data, HttpResponse):
            return cache_data
        response = super().get(request, *args, **kwargs)
        return self.add_cache_headers(response, cache_data)

    def list(self, request, *args, **kwargs):
        # Перевірка на наявність кешування
        cache_data = self.check_cache_headers(request)
        if isinstance(cache_data, HttpResponse):
            return cache_data
        response = super().list(request, *args, **kwargs)
        return self.add_cache_headers(response, cache_data)


@extend_schema_view(
    get=extend_schema(
        parameters=[
            OpenApiParameter(
                name="Accept-Language",
                description=_(
                    "Preferred language for the response. Allowed values: {languages_list}."
                ).format(languages_list=", ".join(settings.PARLER_LANGUAGES_LIST)),
                required=False,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.HEADER,
            )
        ],
    ),
)
@extend_schema(tags=["Category API"])
class CategoriesAPIDetail(MixinCacheHeaders, generics.RetrieveAPIView):
    """Отримати деталі продукту"""

    # queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        """Фільтрація за мовою"""
        lang = get_language_code(self.request)
        result = Categories.objects.language(lang).all()
        return result

    def retrieve(self, request, *args, **kwargs):
        # Перевірка на наявність кешування
        cache_data = self.check_cache_headers(request)
        if isinstance(cache_data, HttpResponse):
            return cache_data
        response = super().retrieve(request, *args, **kwargs)
        return self.add_cache_headers(response, cache_data)


@extend_schema(tags=["Category API"])
class CategoriesAPIUpdate(generics.RetrieveUpdateAPIView):
    """Оновлення продукту"""

    queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Фільтрація за мовою"""
        lang = get_language_code(self.request)
        result = Categories.objects.language(lang).all()
        return result


@extend_schema_view(
    get=extend_schema(
        parameters=[
            OpenApiParameter(
                name="Accept-Language",
                description=_(
                    "Preferred language for the response. Allowed values: {languages_list}."
                ).format(languages_list=", ".join(settings.PARLER_LANGUAGES_LIST)),
                required=False,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.HEADER,
            )
        ],
    ),
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name="Accept-Language",
                description=_(
                    "Preferred language for the response. Allowed values: {languages_list}."
                ).format(languages_list=", ".join(settings.PARLER_LANGUAGES_LIST)),
                required=False,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.HEADER,
            )
        ],
    ),
)
@extend_schema(tags=["Product API"])
class ProductAPIList(MixinCacheHeaders, generics.ListCreateAPIView):
    """Отримати список продуктів або створити новий"""

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        """Фільтрація товарів за мовою"""
        lang = get_language_code(self.request)
        return Product.objects.language(lang).all()

    def get(self, request, *args, **kwargs):
        # Перевірка на наявність кешування
        cache_data = self.check_cache_headers(request)
        if isinstance(cache_data, HttpResponse):
            return cache_data
        response = super().get(request, *args, **kwargs)
        return self.add_cache_headers(response, cache_data)

    def list(self, request, *args, **kwargs):
        # Перевірка на наявність кешування
        cache_data = self.check_cache_headers(request)
        if isinstance(cache_data, HttpResponse):
            return cache_data
        response = super().list(request, *args, **kwargs)
        return self.add_cache_headers(response, cache_data)


@extend_schema_view(
    get=extend_schema(
        parameters=[
            OpenApiParameter(
                name="Accept-Language",
                description=_(
                    "Preferred language for the response. Allowed values: {languages_list}."
                ).format(languages_list=", ".join(settings.PARLER_LANGUAGES_LIST)),
                required=False,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.HEADER,
            )
        ],
    ),
)
@extend_schema(tags=["Product API"])
class ProductAPIDetail(MixinCacheHeaders, generics.RetrieveAPIView):
    """Отримати деталі продукту"""

    # queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        """Фільтрація товарів за мовою"""
        lang = get_language_code(self.request)
        return Product.objects.language(lang).all()

    def retrieve(self, request, *args, **kwargs):
        # Перевірка на наявність кешування
        cache_data = self.check_cache_headers(request)
        if isinstance(cache_data, HttpResponse):
            return cache_data
        response = super().retrieve(request, *args, **kwargs)
        return self.add_cache_headers(response, cache_data)


@extend_schema(tags=["Product API"])
class ProductAPIUpdate(generics.RetrieveUpdateAPIView):
    """Оновлення продукту"""

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (IsAuthenticated,)


@extend_schema(tags=["Tools API"])
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


class CategoriesFilter(django_filters.FilterSet):
    has_length = django_filters.BooleanFilter()
    has_width = django_filters.BooleanFilter()
    has_diameter = django_filters.BooleanFilter()
    has_weight = django_filters.BooleanFilter()

    class Meta:
        model = Categories
        fields = ["has_length", "has_width", "has_diameter", "has_weight"]


# NOT USED
class CategoriesViewSet(viewsets.ModelViewSet):
    """CRUD для продуктів CategoriesViewSet"""

    queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer
    permission_classes = (AllowAny,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = CategoriesFilter

    def get_queryset(self):
        """Фільтрація товарів за мовою"""
        lang = get_language_code(self.request)
        return Categories.objects.language(lang).prefetch_related("translations").all()

    # def retrieve(self, request, *args, **kwargs):
    #     """Отримання продукту за slug з урахуванням мови"""
    #     lang = get_language_code(self.request)
    #     field = "translations__slug"  # Вказуємо, що шукаємо в перекладах
    #     result = get_object_or_404(
    #         Categories, **{field: kwargs["pk"], "translations__language_code": lang}
    #     )
    #     serializer = self.get_serializer(result)
    #     return Response(serializer.data)

    @extend_schema(
        summary="Get example data",
        description="Returns an example response with some data.",
        responses={200: dict},
    )
    def get(self, request):
        return Response({"message": "Hello, API!"})


class SubCategoriesViewSet(viewsets.ModelViewSet):
    """CRUD для продуктів"""

    queryset = SubCategories.objects.all()
    serializer_class = SubCategoriesSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        """Фільтрація товарів за мовою"""
        lang = self.request.GET.get("lang", "uk")
        if lang == "uk":
            return SubCategories.objects.filter(translations__language_code="uk")
        return SubCategories.objects.filter(translations__language_code="en")

    def retrieve(self, request, *args, **kwargs):
        """Отримання продукту за slug з урахуванням мови"""
        lang = request.GET.get("lang", "uk")
        field = "translations__slug"  # Вказуємо, що шукаємо в перекладах
        result = get_object_or_404(
            SubCategories, **{field: kwargs["pk"], "translations__language_code": lang}
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


class DescriptionViewSet(viewsets.ModelViewSet):
    """CRUD для продуктів"""

    serializer_class = DescriptionsSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        """Фільтрація товарів за мовою"""
        lang = get_language_code(self.request)
        return Descriptions.objects.language(lang).all()


class ProductViewSet(viewsets.ModelViewSet):
    """CRUD для продуктів"""

    serializer_class = ProductSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        lang = get_language_code(self.request)
        description_qs = Descriptions.objects.language(lang)
        """Фільтрація товарів за мовою та підвантаження зв'язків"""
        # lang = get_language_code(self.request)
        return (
            Product.objects.language(lang)
            .prefetch_related(
                Prefetch("description", queryset=description_qs),
                "statuses",
                "subproducts",
                "occasions",
                "materials__material",  # якщо є
                "attributes",  # якщо є
                "images",  # якщо є
                "certificates",  # якщо є
                "gemstones",  # якщо є
            )
            .select_related("category", "subcategory", "collection", "design")
        )

    def retrieve(self, request, *args, **kwargs):
        """Отримання продукту за id або slug з урахуванням мови"""
        lookup_value = kwargs.get("pk")  # Отримуємо значення з URL
        lang = request.GET.get("lang", "uk")
        queryset = Product.objects.language(lang)

        # Перевіряємо, чи є lookup_value числом (id) чи текстом (slug)
        try:
            # Якщо це число, шукаємо за id
            lookup_int = int(lookup_value)
            product = get_object_or_404(queryset, id=lookup_int)
        except ValueError:
            # Якщо не число, шукаємо за slug у перекладах
            product = get_object_or_404(queryset, translations__slug=lookup_value)

        serializer = self.get_serializer(product)
        return Response(serializer.data)


class SubProductsSizesViewSet(MixinCacheHeaders, viewsets.ModelViewSet):
    """CRUD для типорозмірів"""

    queryset = SubProducts.objects.all()
    serializer_class = SubProductsSizesSerializer
    permission_classes = (AllowAny,)


class TotalProductsViewSet(ReadOnlyModelViewSet):
    queryset = Product.objects.prefetch_related("subproducts").all()
    serializer_class = TotalProductsSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        """Фільтрація товарів за мовою"""
        lang = get_language_code(self.request)
        return Product.objects.language(lang).all()

    def retrieve(self, request, *args, **kwargs):
        """Отримання продукту за ID разом із його підпродуктами"""
        product = get_object_or_404(Product, id=kwargs["pk"])
        serializer = self.get_serializer(product)
        return Response(serializer.data)

    @extend_schema(
        summary="Get example data",
        description="Returns an example response with some data.",
        responses={200: dict},
    )
    def get(self, request):
        return Response({"message": "Hello, API!"})
