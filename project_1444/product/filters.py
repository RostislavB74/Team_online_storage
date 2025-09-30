import django_filters
from addons.filters import CommaSeparatedIntegerListFilter
from django_filters import rest_framework as filters
from django.db.models import Q
from product.models import Product, Categories
from project_1444.settings import LANGUAGE_CODE


class ProductFilter(filters.FilterSet):
    categories = CommaSeparatedIntegerListFilter(field_name="category_id")
    subcategories = CommaSeparatedIntegerListFilter(field_name="subcategory_id")
    year_collection_range = filters.RangeFilter(field_name="year_collection")
    name = filters.CharFilter(method="filter_name")
    material = filters.CharFilter(field_name="materials__material__material_name", lookup_expr="iexact")
    gemstone = filters.CharFilter(field_name="gemstones__gemstone__name", lookup_expr="iexact")
    price_min = filters.NumberFilter(field_name="subproducts__price", lookup_expr="gte")
    price_max = filters.NumberFilter(field_name="subproducts__price", lookup_expr="lte")
    statuses = filters.CharFilter(method="filter_statuses")

    class Meta:
        model = Product
        fields = (
            "category",
            "subcategory",
            "collection",
            "year_collection",
            "is_ukrainian_cashback",
            "name",
            "material",
            "gemstone",
            "price_min",
            "price_max",
            # "price",
            # "slug",
            # "ean_13",
            # "sku",
            # "article",
            "statuses",
            # "occasions",
            # "description",
            # "subproducts",
            # "gemstone",
            # "material",
            # "images",
            # "certificates",
            # "design",
            # "attributes",
            # "year_collection",
        )

    def filter_name(self, queryset, name, value):
        lang = self.request.GET.get("lang", LANGUAGE_CODE)
        return queryset.filter(
            Q(translations__name__icontains=value) | Q(description__translations__text__icontains=value)
        ).language(lang)

    def filter_description(self, queryset, name, value):
        lang = self.request.GET.get("lang", LANGUAGE_CODE)
        return queryset.filter(description__translations__text__icontains=value).language(lang)

    def filter_statuses(self, queryset, name, value):
        return queryset


class CategoriesFilter(django_filters.FilterSet):
    has_length = django_filters.BooleanFilter()
    has_width = django_filters.BooleanFilter()
    has_diameter = django_filters.BooleanFilter()
    has_weight = django_filters.BooleanFilter()

    class Meta:
        model = Categories
        fields = ["has_length", "has_width", "has_diameter", "has_weight"]
