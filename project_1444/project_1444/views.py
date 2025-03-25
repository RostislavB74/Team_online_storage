import requests
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers

class ApiSchemaSerializer(serializers.Serializer):
    endpoints = serializers.DictField(child=serializers.URLField())

class ApiRootView(APIView):
    serializer_class = ApiSchemaSerializer

    def get(self, request, *args, **kwargs):
        schema_url = request.build_absolute_uri("/api/schema/?format=json")  # Додаємо ?format=json
        try:
            schema_response = requests.get(schema_url, timeout=5)
            schema_response.raise_for_status()
        except requests.RequestException as e:
            return Response({"error": f"Не вдалося отримати API-схему: {str(e)}"}, status=500)

        if not schema_response.text.strip():
            return Response({"error": "Схема порожня", "content": schema_response.text}, status=500)

        try:
            schema = schema_response.json()
        except ValueError as e:
            return Response({"error": "Некоректна API-схема", "content": schema_response.text}, status=500)

        endpoints = {}
        for path, details in schema.get("paths", {}).items():
            for method, method_details in details.items():
                if "operationId" in method_details:
                    endpoints[f"{method.upper()} {path}"] = request.build_absolute_uri(method_details["operationId"])

        serializer = ApiSchemaSerializer({"endpoints": endpoints})
        return Response(serializer.data)