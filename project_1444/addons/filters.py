import django_filters
from rest_framework.exceptions import ValidationError


class CommaSeparatedIntegerListFilter(
    django_filters.BaseInFilter, django_filters.CharFilter
):
    lookup_expr = "in"

    def filter(self, qs, value):
        if not value:
            return qs

        try:
            cleaned = [int(v) for v in value]
        except ValueError:
            raise ValidationError(
                {
                    self.field_name.split("_")[0]: [
                        "Expected comma-separated integers in filters"
                    ]
                }
            )

        return super().filter(qs, cleaned)
