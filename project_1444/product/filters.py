import django_filters

from product.models import Product, Categories


class ProductFilter(django_filters.FilterSet):
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
