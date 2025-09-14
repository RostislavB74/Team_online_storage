from django.contrib import admin
from parler.admin import TranslatableAdmin

from project_1444.settings import LANGUAGE_CODE
from tcategories.models import TCategories


@admin.register(TCategories)
class TCategoriesAdmin(TranslatableAdmin):
    list_display = ("id", "name", "parent", "display_full_path")
    search_fields = ("translations__name",)
    readonly_fields = ("display_full_path",)
    list_display_links = ("id", "name")
    list_filter = ("parent",)
    list_select_related = ("parent",)

    def get_name(self, obj):
        return obj.pk

    def get_prepopulated_fields(self, request, obj=None):
        return {"slug": ("name",)}

    @admin.display(description="Full Path")
    def display_full_path(self, obj):
        return obj.get_full_path(obj.language_code)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "parent":
            queryset = db_field.related_model.objects.all()
            if request.resolver_match.kwargs.get("object_id"):
                queryset = queryset.exclude(
                    id=request.resolver_match.kwargs.get("object_id")
                )
            kwargs["queryset"] = queryset
        field = super().formfield_for_foreignkey(db_field, request, **kwargs)

        if db_field.name == "parent":
            lang = request.GET.get("language")
            if not lang or lang == LANGUAGE_CODE:
                return field

            def label_from_instance(obj):
                field_translated = obj.safe_translation_getter(
                    "name",
                    language_code=lang,
                    any_language=True,
                )
                return f"{obj.pk:03d}-{field_translated}"

            field.label_from_instance = label_from_instance

        return field
