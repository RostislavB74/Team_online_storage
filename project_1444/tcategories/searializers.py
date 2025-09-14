from rest_framework import serializers

from tcategories.models import TCategories


class TCategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TCategories
        fields = ["id", "name", "slug", "parent_id"]  # noqa


class TCategoryShortSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    slug = serializers.CharField()

    class Meta:
        model = TCategories
        fields = ["id", "name", "slug"]


class TCategoryFullPathSerializer(serializers.ModelSerializer):
    full_path = serializers.SerializerMethodField()

    class Meta:
        model = TCategories
        fields = ["id", "name", "slug", "parent_id", "full_path"]  # noqa
        read_only_fields = ["full_path"]

    @staticmethod
    def get_full_path(obj):
        return obj.get_full_path()
