import django_filters

from addons.filters import CommaSeparatedIntegerListFilter
from product.models import Product, Categories


class ProductFilter(django_filters.FilterSet):
    category_list = CommaSeparatedIntegerListFilter(field_name="category_id")
    subcategory_list = CommaSeparatedIntegerListFilter(field_name="subcategory_id")
    year_collection_range = django_filters.RangeFilter(field_name="year_collection")

    class Meta:
        model = Product
        fields = (
            "category",
            "subcategory",
            "collection",
            "year_collection",
            "is_ukrainian_cashback",
        )


class CategoriesFilter(django_filters.FilterSet):
    has_length = django_filters.BooleanFilter()
    has_width = django_filters.BooleanFilter()
    has_diameter = django_filters.BooleanFilter()
    has_weight = django_filters.BooleanFilter()

    class Meta:
        model = Categories
        fields = ["has_length", "has_width", "has_diameter", "has_weight"]
