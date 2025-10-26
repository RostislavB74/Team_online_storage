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
from addons.filters import CommaSeparatedIntegerListFilter


class ProductFilter(filters.FilterSet):
    categories = CommaSeparatedIntegerListFilter(field_name="category_id")
    subcategories = CommaSeparatedIntegerListFilter(field_name="subcategory_id")
    year_collection_range = filters.RangeFilter(field_name="year_collection")
    name = filters.CharFilter(method="filter_name")
    material_name = filters.CharFilter(method="filter_material_name")
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
    size = filters.CharFilter(method="filter_size")
    # gender = filters.CharFilter(method="filter_gender")
    gender = filters.CharFilter(method="filter_gender", help_text="Фільтр за гендером (female, male, unisex, children)")

    class Meta:
        model = Product
        fields = (
            "category_id",  #
            "subcategory_id",  #
            "collection_id",  #
            "year_collection",
            "is_ukrainian_cashback",
            "gender",
        )

    def filter_name(self, queryset, name, value):
        lang = get_language_code(self.request)
        return (
            queryset.filter(
                Q(translations__name__icontains=value) | Q(description__translations__text__icontains=value)
            ).translated(lang)
            # .distinct()
        )

    def filter_material_name(self, queryset, name, value):
        lang = get_language_code(self.request)
        return queryset.filter(materials__material__translations__material_name__iexact=value).translated(
            lang
        )  # .distinct()

    def filter_color_name(self, queryset, name, value):
        lang = get_language_code(self.request)
        return queryset.filter(materials__material__translations__color_name__iexact=value).translated(
            lang
        )  # .distinct()

    def filter_gemstone(self, queryset, name, value):
        lang = get_language_code(self.request)
        return queryset.filter(gemstones__gemstone__translations__name__iexact=value).translated(lang)  # .distinct()

    def filter_statuses(self, queryset, name, value):
        lang = get_language_code(self.request)
        statuses = value.split(",")
        return queryset.filter(statuses__translations__name__in=statuses).translated(lang)  # .distinct()

    def filter_collection(self, queryset, name, value):
        lang = get_language_code(self.request)
        return queryset.filter(collection__translations__name__icontains=value).translated(lang)  # .distinct()

    def filter_design(self, queryset, name, value):
        lang = get_language_code(self.request)
        return queryset.filter(design__translations__name__icontains=value).translated(lang)  # .distinct()

    def filter_occasions(self, queryset, name, value):
        lang = get_language_code(self.request)
        occasions = value.split(",")
        return queryset.filter(occasions__translations__name__in=occasions).translated(lang)  # .distinct()

    def filter_year_collection(self, queryset, name, value):
        return queryset.filter(year_collection=value)  # .distinct()

    def filter_subproducts(self, queryset, name, value):
        subproducts = value.split(",")
        return queryset.filter(subproducts__article__in=subproducts)  # .distinct()

    def filter_size(self, queryset, name, value):
        # Нормалізуємо значення: замінюємо ',' на '.' і перетворюємо на float
        normalized_value = value.replace(",", ".")
        try:
            size_float = float(normalized_value)
        except ValueError:
            return queryset.none()  # Якщо не вдалося перетворити, повертаємо пустий queryset

        return queryset.filter(
            Q(subproducts__size__gte=size_float - 0.25) & Q(subproducts__size__lte=size_float + 0.25)
            | Q(subproducts__length__gte=size_float - 0.25) & Q(subproducts__length__lte=size_float + 0.25)
            | Q(subproducts__max_length__gte=size_float - 0.25) & Q(subproducts__max_length__lte=size_float + 0.25)
        )  # .distinct()

    def filter_gender(self, queryset, name, value):
        """Фільтр за гендером (через кому, якщо декілька значень)."""
        genders = [v.strip().lower() for v in value.split(",")]
        return queryset.filter(attributes__gender__in=genders)


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
        return queryset.filter(translations__name__icontains=value).translated(lang)  # .distinct()


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
        return queryset.filter(translations__material_name__iexact=value).translated(lang)  # .distinct()

    def filter_color_name(self, queryset, name, value):
        lang = get_language_code(self.request)
        return queryset.filter(translations__color_name__iexact=value).translated(lang)  # .distinct()


class GemstonesFilter(filters.FilterSet):
    name = filters.CharFilter(method="filter_name")

    class Meta:
        model = Gemstone
        fields = []  # Видалено "name", бо це не фізичне поле

    def filter_name(self, queryset, name, value):
        lang = get_language_code(self.request)
        return queryset.filter(translations__name__iexact=value).translated(lang)  # .distinct()


class OccasionsFilter(django_filters.FilterSet):
    name = filters.CharFilter(method="filter_name")

    class Meta:
        model = Occasion
        fields = ["name"]

    def filter_name(self, queryset, name, value):
        lang = get_language_code(self.request)
        return queryset.filter(translations__name__iexact=value).translated(lang)  # .distinct()


class CollectionsFilter(django_filters.FilterSet):
    name = filters.CharFilter(method="filter_name")

    class Meta:
        model = Collections
        fields = ["name"]

    def filter_name(self, queryset, name, value):
        lang = get_language_code(self.request)
        return queryset.filter(translations__name__iexact=value).translated(lang)  # .distinct()
