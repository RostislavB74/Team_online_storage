import requests
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers
import logging

logger = logging.getLogger(__name__)

class ApiSchemaSerializer(serializers.Serializer):
    endpoints = serializers.DictField(child=serializers.URLField())

class ApiRootView(APIView):
    serializer_class = ApiSchemaSerializer

    def get(self, request, *args, **kwargs):
        # Спробуємо отримати схему з кешу
        cache_key = "api_schema_json"
        schema = cache.get(cache_key)
        
        if schema is None:
            schema_url = request.build_absolute_uri("/api/schema/?format=json")
            logger.info(f"Cache miss, requesting schema from: {schema_url}")
            try:
                schema_response = requests.get(schema_url, timeout=15)
                schema_response.raise_for_status()
                logger.info(f"Schema received, status: {schema_response.status_code}")
            except requests.RequestException as e:
                logger.error(f"Failed to fetch schema: {str(e)}")
                return Response({"error": f"Не вдалося отримати API-схему: {str(e)}"}, status=500)

            if not schema_response.text.strip():
                logger.warning("Schema response is empty")
                return Response({"error": "Схема порожня", "content": schema_response.text}, status=500)

            try:
                schema = schema_response.json()
                logger.info("Schema parsed successfully")
                # Зберігаємо в кеш на 1 годину (3600 секунд)
                cache.set(cache_key, schema, timeout=3600)
            except ValueError as e:
                logger.error(f"Invalid schema format: {str(e)}")
                return Response({"error": "Некоректна API-схема", "content": schema_response.text}, status=500)
        else:
            logger.info("Schema retrieved from cache")

        endpoints = {}
        for path, details in schema.get("paths", {}).items():
            for method, method_details in details.items():
                if "operationId" in method_details:
                    endpoints[f"{method.upper()} {path}"] = request.build_absolute_uri(method_details["operationId"])

        serializer = ApiSchemaSerializer({"endpoints": endpoints})
        return Response(serializer.data)