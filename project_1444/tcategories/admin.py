from django.contrib import admin
from parler.admin import TranslatableAdmin

from project_1444.settings import LANGUAGE_CODE
from tcategories.models import TCategories


@admin.register(TCategories)
class TCategoriesAdmin(TranslatableAdmin):
    list_display = ("id", "name", "slug", "display_full_path")
    search_fields = ("name",)
    readonly_fields = ("display_full_path",)

    def get_prepopulated_fields(self, request, obj=None):
        return {"slug": ("name",)}

    def get_queryset(self, request):
        lang = request.GET.get("language") or "en"
        # print(f"get_queryset {lang=}")
        qs = TCategories.objects.language(lang).all()
        return qs

    @admin.display(description="Full Path")
    def display_full_path(self, obj):
        return obj.get_full_path()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "parent":
            queryset = db_field.related_model.objects.all().order_by("pk")
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
                # field_translated = obj.safe_translation_getter(
                #     "name",
                #     language_code=lang,
                #     any_language=True,
                # )
                field_translated = getattr(obj, "name")
                return f"{obj.pk:03d}-{field_translated}"

            field.label_from_instance = label_from_instance

        return field
