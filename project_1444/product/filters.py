import django_filters
from addons.filters import CommaSeparatedIntegerListFilter
from django_filters import rest_framework as filters
from django.db.models import Q
from product.models import Product, Categories, SubCategories, Collections

from django_filters import rest_framework as filters
from django.db.models import Q
from product.models import Product, Descriptions


class CommaSeparatedIntegerListFilter(filters.BaseCSVFilter, filters.NumberFilter):
    def filter(self, qs, value):
        if value:
            return qs.filter(**{f"{self.field_name}__in": value})
        return qs


from django_filters import rest_framework as filters
from django.db.models import Q
from product.models import Product, Descriptions


class CommaSeparatedIntegerListFilter(filters.BaseCSVFilter, filters.NumberFilter):
    def filter(self, qs, value):
        if value:
            return qs.filter(**{f"{self.field_name}__in": value})
        return qs


class ProductFilter(filters.FilterSet):
    categories = CommaSeparatedIntegerListFilter(field_name="category_id")
    subcategories = CommaSeparatedIntegerListFilter(field_name="subcategory_id")
    year_collection_range = filters.RangeFilter(field_name="year_collection")
    name = filters.CharFilter(method="filter_name")
    material = filters.CharFilter(
        field_name="materials__material__material_name", lookup_expr="iexact"
    )
    gemstone = filters.CharFilter(
        field_name="gemstones__gemstone__name", lookup_expr="iexact"
    )
    price_min = filters.NumberFilter(field_name="subproducts__price", lookup_expr="gte")
    price_max = filters.NumberFilter(field_name="subproducts__price", lookup_expr="lte")

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
        )

    def filter_name(self, queryset, name, value):
        lang = self.request.GET.get("lang", "uk")
        return queryset.filter(
            Q(translations__name__icontains=value)
            | Q(description__translations__text__icontains=value)
        ).language(lang)

    def filter_description(self, queryset, name, value):
        lang = self.request.GET.get("lang", "uk")
        return queryset.filter(description__translations__text__icontains=value).language(lang)

# class CommaSeparatedIntegerListFilter(filters.BaseCSVFilter, filters.NumberFilter):
#     """Кастомний фільтр для списку цілих чисел, розділених комами"""

#     def filter(self, qs, value):
#         if value:
#             return qs.filter(**{f"{self.field_name}__in": value})
#         return qs


# class ProductFilter(filters.FilterSet):
#     categories = CommaSeparatedIntegerListFilter(field_name="category_id")
#     subcategories = CommaSeparatedIntegerListFilter(field_name="subcategory_id")
#     year_collection_range = filters.RangeFilter(field_name="year_collection")
#     name = filters.CharFilter(method="filter_name")  # Пошук за назвою
#     material = filters.CharFilter(
#         field_name="materials__material__name", lookup_expr="iexact"
#     )  # Фільтр за матеріалом
#     gemstone = filters.CharFilter(
#         field_name="gemstones__name", lookup_expr="iexact"
#     )  # Фільтр за каменем
#     price_min = filters.NumberFilter(field_name="price", lookup_expr="gte")  # Ціна від
#     price_max = filters.NumberFilter(field_name="price", lookup_expr="lte")  # Ціна до

#     class Meta:
#         model = Product
#         fields = (
#             "category",
#             "subcategory",
#             "collection",
#             "year_collection",
#             "is_ukrainian_cashback",
#             "name",
#             "material",
#             "gemstone",
#             "price_min",
#             "price_max",
#         )

#     def filter_name(self, queryset, name, value):
#         """Пошук за назвою та описом з урахуванням локалізації"""
#         lang = self.request.GET.get(
#             "lang", "uk"
#         )  # Припускаємо, що мова передається в запиті
#         return queryset.filter(
#             Q(translations__name__icontains=value)
#             | Q(description__text__icontains=value)
#         ).language(lang)


class CategoriesFilter(django_filters.FilterSet):
    has_length = django_filters.BooleanFilter()
    has_width = django_filters.BooleanFilter()
    has_diameter = django_filters.BooleanFilter()
    has_weight = django_filters.BooleanFilter()

    class Meta:
        model = Categories
        fields = ["has_length", "has_width", "has_diameter", "has_weight"]
