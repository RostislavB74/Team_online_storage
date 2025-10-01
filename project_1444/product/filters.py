import django_filters
from addons.filters import CommaSeparatedIntegerListFilter
from django_filters import rest_framework as filters
from django.db.models import Q
from product.models import Product, Categories, Material, Gemstone, SubProducts, Occasion
#category
# price
# metal color
# material
# size
# collection (for her/ for him/ for kids)
# gemstone
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
    statuses  = filters.CharFilter(method="filter_statuses")
    collection=filters.CharFilter(method="filter_collection")
    design=filters.CharFilter(method="filter_design")
    occasions=filters.CharFilter(method="filter_occasions")
    year_collection=filters.CharFilter(method="filter_year_collection")
    subcategories = filters.CharFilter(method="filter_subcategories")
    subproducts = filters.CharFilter(method="filter_subproducts")

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
            "statuses",
            "occasions",
            "subproducts",
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



class CategoriesFilter(django_filters.FilterSet):
    has_length = django_filters.BooleanFilter()
    has_width = django_filters.BooleanFilter()
    has_diameter = django_filters.BooleanFilter()
    has_weight = django_filters.BooleanFilter()

    class Meta:
        model = Categories
        fields = ["has_length", "has_width", "has_diameter", "has_weight"]
class MaterialsFilter(django_filters.FilterSet):
    class Meta:
        model = Material
        fields = ["assay", "color", "article"]

class GemstonesFilter(django_filters.FilterSet):
    class Meta:
        model = Gemstone
        fields = ["name"]

class OccasionsFilter(django_filters.FilterSet):
    class Meta:
        model = Occasion
        fields = ["name"]