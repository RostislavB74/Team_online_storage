from rest_framework import serializers


class HealthCheckSerializer(serializers.Serializer):
    status = serializers.CharField(max_length=10)


class VersionSerializer(serializers.Serializer):
    git_version = serializers.CharField(max_length=50)
    version = serializers.CharField(max_length=50)
