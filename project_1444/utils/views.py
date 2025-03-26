from django.conf import settings
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.serializers import HealthCheckSerializer, VersionSerializer


@extend_schema(tags=["api"])
class HealthCheckView(APIView):
    serializer_class = HealthCheckSerializer

    def get(self, request):
        return Response({"status": "ok"})


@extend_schema(tags=["api"])
class VersionView(APIView):
    serializer_class = VersionSerializer

    def get(self, request):
        return Response(
            {"git_version": settings.GIT_VERSION, "version": settings.VERSION}
        )
