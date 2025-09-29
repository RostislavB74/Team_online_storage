from hashlib import md5
from urllib.parse import urlencode

from django.conf import settings
from django.core.cache import cache
from django.db import IntegrityError
from django.db.models import F
from django.db.models import Prefetch
from django.db.models.functions import Abs
from django.http import HttpResponseNotModified
from django.shortcuts import get_object_or_404
from django.utils.http import quote_etag
from django.utils.translation import gettext as _
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)
from rest_framework import status
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter
from rest_framework.permissions import (
    AllowAny,
)
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from product.filters import CategoriesFilter, ProductFilter
from product.models import (
    Product,
    RingSizeConversion,
    Categories,
    SubProducts,
    Descriptions,
    SubCategories,
)
from product.permissions import IsAdminOrReadOnly
from product.serializers import (
    ProductSerializer,
    RingSizeSerializer,
    SubProductsSizesSerializer,
    DescriptionsSerializer,
    TotalProductsSerializer,
    SubCategoriesSerializer,
    CategoriesTreeSerializer,
)
from utils.language_code import get_language_code


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = (AllowAny,)
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = ProductFilter
    search_fields = ["translations__name", "description__translations__text"]
    ordering_fields = [
        "category__translations__name",
        "subcategory__translations__name",
        "collection__translations__name",
        "year_collection",
        "is_ukrainian_cashback",
        "subproducts__price",  # Оновлено
    ]
    ordering = ["category__translations__name"]

    def get_queryset(self):
        lang = get_language_code(self.request)
        description_qs = Descriptions.objects.language(lang)
        return (
            Product.objects.language(lang)
            .prefetch_related(
                Prefetch("description", queryset=description_qs),
                "statuses",
                "subproducts",
                "occasions",
                "materials__material",
                "attributes",
                "images",
                "certificates",
                "gemstones",
                "translations",
            )
            .select_related("category", "subcategory", "collection", "design")
        )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        content = str(data).encode("utf-8")
        etag = quote_etag(md5(content).hexdigest())
        if request.headers.get("If-None-Match") == etag:
            return HttpResponseNotModified()
        response = Response(data)
        response["ETag"] = etag
        response["Cache-Control"] = "max-age=3600"
        return response


@extend_schema(tags=["Tools API"])
class RingSizeLookup(APIView):
    """Переводить окружність пальця в розмір кільця, знаходячи найближче значення"""

    serializer_class = RingSizeSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="circumference",
                description=_("Окружність пальця в міліметрах (напр. 60)"),
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
                {"error": _("Circumference is required")},
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
                    {"error": _("No sizes available")}, status=status.HTTP_404_NOT_FOUND
                )

        except ValueError:
            return Response(
                {"error": _("Invalid circumference value")},
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


# USED
@extend_schema(tags=["Categories"])
class CategoriesViewSet(viewsets.ModelViewSet):
    """CRUD для категорій"""

    queryset = Categories.objects.all()
    serializer_class = CategoriesTreeSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = CategoriesFilter
    ordering_fields=["name"]
    ordering=["name"]
    # ordering_fields = [
    #     "translations__name",
    # ]
    # ordering = ["translations__name"]
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer]
    pagination_class = None

    def get_queryset(self):
        """Фільтрація товарів за мовою"""
        lang = get_language_code(self.request)
        qs = Categories.objects.translated(lang)

        # qs = Categories.objects.language(lang)
        if self.action == "list":
            return qs.prefetch_related(
                "translations", "subcategories", "subcategories__translations"
            ).order_by('name')
        return qs

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except IntegrityError as e:
            raise ValidationError({"detail": f"Category creation failed: {str(e)}"})

    def get_cache_key(self):
        """
        Build cache key based on request path, language, and ALL query parameters.
        This automatically includes any filter parameters since they come via GET.
        """
        components = [
            self.request.path,
            get_language_code(self.request),
            urlencode(sorted(self.request.GET.items())),  # All sorted params
        ]

        # Create hash-based key
        key_string = "|".join(str(c) for c in components)
        return f"category_tree_{md5(key_string.encode()).hexdigest()}"

    def list(self, request, *args, **kwargs):
        cache_key = self.get_cache_key()
        cached_response = cache.get(cache_key)
        if cached_response is not None:
            # print("Using cached response", cache_key)
            return Response(cached_response)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, settings.SQL_CACHE_TIMEOUT_DEFAULT)
        # print("Added cached response", cache_key)
        return response


@extend_schema(tags=["Categories"])
class SubCategoriesViewSet(viewsets.ModelViewSet):
    """CRUD для продуктів"""

    queryset = SubCategories.objects.all()
    serializer_class = SubCategoriesSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


    def get_queryset(self):
        """Фільтрація товарів за мовою"""
        lang = get_language_code(self.request)
        qs = SubCategories.objects.language(lang)
        if self.action == "list":
            return qs.prefetch_related("translations")
        return qs.all()

    def retrieve(self, request, *args, **kwargs):
        """Отримання продукту за slug з урахуванням мови"""
        lang = get_language_code(self.request)
        field = "translations__slug"  # Вказуємо, що шукаємо в перекладах
        result = get_object_or_404(
            SubCategories, **{field: kwargs["pk"], "translations__language_code": lang}
        )
        serializer = self.get_serializer(result)
        return Response(serializer.data)

    @extend_schema(
        summary=_("Get example data"),
        description=_("Returns an example response with some data."),
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
        qs = Descriptions.objects.language(lang)
        if self.action == "list":
            return qs.prefetch_related("translations")
        return qs.all()


class SubProductsSizesViewSet(viewsets.ModelViewSet):
    """CRUD для типорозмірів"""

    queryset = SubProducts.objects.all()
    serializer_class = SubProductsSizesSerializer
    permission_classes = (AllowAny,)


class TotalProductsViewSet(ReadOnlyModelViewSet):
    queryset = Product.objects.prefetch_related("subproducts")
    serializer_class = TotalProductsSerializer
    permission_classes = (AllowAny,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter

    def get_queryset(self):
        """Фільтрація товарів за мовою"""
        lang = get_language_code(self.request)
        qs = super().get_queryset().language(lang)
        if self.action == "list":
            return qs.prefetch_related("translations")
        return qs.all()

    def retrieve(self, request, *args, **kwargs):
        """Отримання продукту за ID разом із його підпродуктами"""
        product = get_object_or_404(Product, id=kwargs["pk"])
        serializer = self.get_serializer(product)
        return Response(serializer.data)

    @extend_schema(
        summary=_("Get example data"),
        description=_("Returns an example response with some data."),
        responses={200: dict},
    )
    def get(self, request):
        return Response({"message": "Hello, API!"})
