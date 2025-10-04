import django_filters
from django_filters import rest_framework as filters
from django.db.models import Q

# from project_1444.settings import LANGUAGE_CODE
from product.models import (
    Product,
    Categories,
    Material,
    Gemstone,
    # SubProducts,
    Occasion,
    Collections,
    # Styles,
)
from utils.language_code import get_language_code
from addons.filters import CommaSeparatedIntegerListFilter  # Імпортуємо твою функцію


class ProductFilter(filters.FilterSet):
    categories = CommaSeparatedIntegerListFilter(field_name="category_id")
    subcategories = CommaSeparatedIntegerListFilter(field_name="subcategory_id")
    year_collection_range = filters.RangeFilter(field_name="year_collection")
    name = filters.CharFilter(method="filter_name")
    material = filters.CharFilter(method="filter_material")
    material_name = filters.CharFilter(method="filter_material_name")
    color = filters.CharFilter(method="filter_color")
    color_name = filters.CharFilter(method="filter_color_name")
    gemstone = filters.CharFilter(method="filter_gemstone")
    price_min = filters.NumberFilter(field_name="subproducts__price", lookup_expr="gte")
    price_max = filters.NumberFilter(field_name="subproducts__price", lookup_expr="lte")
    statuses = filters.CharFilter(method="filter_statuses")
    collection = filters.CharFilter(method="filter_collection")
    design = filters.CharFilter(method="filter_design")
    occasions = filters.CharFilter(method="filter_occasions")
    year_collection = filters.CharFilter(method="filter_year_collection")
    subproducts = filters.CharFilter(method="filter_subproducts")

    class Meta:
        model = Product
        fields = (
            "category_id",  # Змінено з "category"
            "subcategory_id",  # Змінено з "subcategory"
            "collection_id",  # Змінено з "collection", якщо collection — ForeignKey
            "year_collection",
            "is_ukrainian_cashback",
        )

    def filter_name(self, queryset, name, value):
        lang = get_language_code(self.request)
        return (
            queryset.filter(
                Q(translations__name__icontains=value) | Q(description__translations__text__icontains=value)
            )
            .translated(lang)
            .distinct()
        )

    def filter_material(self, queryset, name, value):
        return queryset.filter(materials__material__material=value).distinct()

    def filter_material_name(self, queryset, name, value):
        lang = get_language_code(self.request)
        return (
            queryset.filter(materials__material__translations__material_name__iexact=value).translated(lang).distinct()
        )

    def filter_color(self, queryset, name, value):
        return queryset.filter(materials__material__color=value).distinct()

    def filter_color_name(self, queryset, name, value):
        lang = get_language_code(self.request)
        return queryset.filter(materials__material__translations__color_name__iexact=value).translated(lang).distinct()

    def filter_gemstone(self, queryset, name, value):
        lang = get_language_code(self.request)
        return queryset.filter(gemstones__gemstone__translations__name__iexact=value).translated(lang).distinct()

    def filter_statuses(self, queryset, name, value):
        lang = get_language_code(self.request)
        statuses = value.split(",")
        return queryset.filter(statuses__translations__name__in=statuses).translated(lang).distinct()

    def filter_collection(self, queryset, name, value):
        lang = get_language_code(self.request)
        return queryset.filter(collection__translations__name__icontains=value).translated(lang).distinct()

    def filter_design(self, queryset, name, value):
        lang = get_language_code(self.request)
        return queryset.filter(design__translations__name__icontains=value).translated(lang).distinct()

    def filter_occasions(self, queryset, name, value):
        lang = get_language_code(self.request)
        occasions = value.split(",")
        return queryset.filter(occasions__translations__name__in=occasions).translated(lang).distinct()

    def filter_year_collection(self, queryset, name, value):
        return queryset.filter(year_collection=value).distinct()

    def filter_subproducts(self, queryset, name, value):
        subproducts = value.split(",")
        return queryset.filter(subproducts__article__in=subproducts).distinct()


# class ProductFilter(filters.FilterSet):
#     categories = CommaSeparatedIntegerListFilter(field_name="category_id")
#     subcategories = CommaSeparatedIntegerListFilter(field_name="subcategory_id")
#     year_collection_range = filters.RangeFilter(field_name="year_collection")
#     name = filters.CharFilter(method="filter_name")
#     material = filters.CharFilter(method="filter_material")
#     gemstone = filters.CharFilter(method="filter_gemstone")
#     price_min = filters.NumberFilter(field_name="subproducts__price", lookup_expr="gte")
#     price_max = filters.NumberFilter(field_name="subproducts__price", lookup_expr="lte")
#     statuses = filters.CharFilter(method="filter_statuses")
#     collection = filters.CharFilter(method="filter_collection")
#     design = filters.CharFilter(method="filter_design")
#     occasions = filters.CharFilter(method="filter_occasions")
#     year_collection = filters.CharFilter(method="filter_year_collection")
#     subproducts = filters.CharFilter(method="filter_subproducts")

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
#             "statuses",
#             "occasions",
#             "subproducts",
#         )

#     def filter_name(self, queryset, name, value):
#         lang = get_language_code(self.request)
#         return (
#             queryset.filter(
#                 Q(translations__name__icontains=value)
#                 | Q(description__translations__text__icontains=value)
#             )
#             .translated(lang)
#             .distinct()
#         )

#     def filter_material(self, queryset, name, value):
#         lang = get_language_code(self.request)
#         return (
#             queryset.filter(
#                 materials__material__translations__material_name__iexact=value
#             )
#             .translated(lang)
#             .distinct()
#         )

#     def filter_gemstone(self, queryset, name, value):
#         lang = get_language_code(self.request)
#         return (
#             queryset.filter(gemstones__gemstone__translations__name__iexact=value)
#             .translated(lang)
#             .distinct()
#         )

#     def filter_statuses(self, queryset, name, value):
#         # Припустимо, statuses — це список через кому, наприклад, "available,sold_out"
#         statuses = value.split(",")
#         return queryset.filter(status__in=statuses).distinct()

#     def filter_collection(self, queryset, name, value):
#         lang = get_language_code(self.request)
#         return (
#             queryset.filter(translations__collection__icontains=value)
#             .translated(lang)
#             .distinct()
#         )

#     def filter_design(self, queryset, name, value):
#         lang = get_language_code(self.request)
#         return (
#             queryset.filter(translations__design__icontains=value)
#             .translated(lang)
#             .distinct()
#         )

#     def filter_occasions(self, queryset, name, value):
#         lang = get_language_code(self.request)
#         occasions = value.split(",")
#         return (
#             queryset.filter(occasions__translations__name__in=occasions)
#             .translated(lang)
#             .distinct()
#         )

#     def filter_year_collection(self, queryset, name, value):
#         return queryset.filter(year_collection=value).distinct()

#     def filter_subproducts(self, queryset, name, value):
#         # Припустимо, subproducts фільтруються за артикулом або ID
#         subproducts = value.split(",")
#         return queryset.filter(subproducts__article__in=subproducts).distinct()


class CategoriesFilter(django_filters.FilterSet):
    has_length = django_filters.BooleanFilter()
    has_width = django_filters.BooleanFilter()
    has_diameter = django_filters.BooleanFilter()
    has_weight = django_filters.BooleanFilter()
    name = filters.CharFilter(method="filter_name")

    class Meta:
        model = Categories
        fields = ["has_length", "has_width", "has_diameter", "has_weight", "name"]

    def filter_name(self, queryset, name, value):
        lang = get_language_code(self.request)
        return queryset.filter(translations__name__icontains=value).translated(lang).distinct()


class MaterialsFilter(filters.FilterSet):
    assay = filters.CharFilter(lookup_expr="exact")
    # color = filters.CharFilter(lookup_expr="exact")
    article = filters.CharFilter(lookup_expr="exact")
    # material = filters.CharFilter(lookup_expr="exact")
    material_name = filters.CharFilter(method="filter_material_name")
    color_name = filters.CharFilter(method="filter_color_name")

    class Meta:
        model = Material
        fields = [
            "assay",
            "color",
            "article",
            "material",
            "material_name",
            "color_name",
        ]

    def filter_material_name(self, queryset, name, value):
        lang = get_language_code(self.request)
        return queryset.filter(translations__material_name__iexact=value).translated(lang).distinct()

    def filter_color_name(self, queryset, name, value):
        lang = get_language_code(self.request)
        return queryset.filter(translations__color_name__iexact=value).translated(lang).distinct()


class GemstonesFilter(filters.FilterSet):
    name = filters.CharFilter(method="filter_name")

    class Meta:
        model = Gemstone
        fields = []  # Видалено "name", бо це не фізичне поле

    def filter_name(self, queryset, name, value):
        lang = get_language_code(self.request)
        return queryset.filter(translations__name__iexact=value).translated(lang).distinct()


class OccasionsFilter(django_filters.FilterSet):
    name = filters.CharFilter(method="filter_name")

    class Meta:
        model = Occasion
        fields = ["name"]

    def filter_name(self, queryset, name, value):
        lang = get_language_code(self.request)
        return queryset.filter(translations__name__iexact=value).translated(lang).distinct()


class CollectionsFilter(django_filters.FilterSet):
    name = filters.CharFilter(method="filter_name")

    class Meta:
        model = Collections
        fields = ["name"]

    def filter_name(self, queryset, name, value):
        lang = get_language_code(self.request)
        return queryset.filter(translations__name__iexact=value).translated(lang).distinct()
