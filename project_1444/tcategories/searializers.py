from django.utils.translation import gettext as _
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from tcategories.models import TCategories


class TCategoriesSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()

    class Meta:
        model = TCategories
        fields = ["id", "name", "slug", "parent_id"]

    @extend_schema_field(str)
    def get_name(self, obj):
        return obj.safe_translation_getter("name", default=_("Без назви"))

    @extend_schema_field(str)
    def get_slug(self, obj):
        return obj.safe_translation_getter("slug", default=None)


class TCategoryShortSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    slug = serializers.CharField()

    class Meta:
        model = TCategories
        fields = ["id", "name", "slug"]
