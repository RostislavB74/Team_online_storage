import requests
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_spectacular.views import SpectacularAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework.test import APIRequestFactory


import logging

logger = logging.getLogger(__name__)


class ApiSchemaSerializer(serializers.Serializer):
    endpoints = serializers.DictField(child=serializers.URLField())


class ApiRootView(APIView):
    serializer_class = ApiSchemaSerializer

    @method_decorator(cache_page(30 * 60, key_prefix="api_root"))  # 30 min
    def get(self, request, *args, **kwargs):
        factory = APIRequestFactory()
        try:
            # schema_response = requests.get(schema_url, timeout=5)
            # schema_response.raise_for_status()
            request_factory = factory.get(reverse("schema"))
            view = SpectacularAPIView.as_view()
            response = view(request_factory)
            response.render()
            schema_response = response.content.decode("utf-8")
        except requests.RequestException as e:
            return Response(
                {"error": f"Не вдалося отримати API-схему: {str(e)}"}, status=500
            )

        if not schema_response.strip():
            return Response(
                {"error": "Схема порожня", "content": schema_response}, status=500
            )

        try:
            schema = response.data
        except ValueError as e:
            return Response(
                {"error": "Некоректна API-схема", "content": schema_response},
                status=500,
            )

        endpoints = {}
        for path, details in schema.get("paths", {}).items():
            for method, method_details in details.items():
                # Отримуємо параметри для заміни
                params = method_details.get("parameters", [])
                resolved_path = path
                for param in params:
                    if param.get("in") == "path":
                        param_name = param["name"]
                        # Приклад значення залежно від типу
                        param_type = param["schema"]["type"]
                        example_value = "12" if param_type == "integer" else "example"
                        resolved_path = resolved_path.replace(
                            f"{{{param_name}}}", example_value
                        )
                endpoints[f"{method.upper()} {path}"] = request.build_absolute_uri(
                    resolved_path
                )

        serializer = ApiSchemaSerializer({"endpoints": endpoints})
        return Response(serializer.data)


# class ApiSchemaSerializer(serializers.Serializer):
#     endpoints = serializers.DictField(child=serializers.URLField())

# class ApiRootView(APIView):
#     serializer_class = ApiSchemaSerializer

#     def get(self, request, *args, **kwargs):
#         schema_url = request.build_absolute_uri("/api/schema/?format=json")
#         try:
#             schema_response = requests.get(schema_url, timeout=5)
#             schema_response.raise_for_status()
#         except requests.RequestException as e:
#             return Response({"error": f"Не вдалося отримати API-схему: {str(e)}"}, status=500)

#         if not schema_response.text.strip():
#             return Response({"error": "Схема порожня", "content": schema_response.text}, status=500)

#         try:
#             schema = schema_response.json()
#         except ValueError as e:
#             return Response({"error": "Некоректна API-схема", "content": schema_response.text}, status=500)

#         endpoints = {}
#         for path, details in schema.get("paths", {}).items():
#             for method, method_details in details.items():
#                 # Якщо шлях містить параметр, залишаємо його як шаблон
#                 if "{" in path and "}" in path:
#                     endpoints[f"{method.upper()} {path}"] = f"{request.scheme}://{request.get_host()}{path}"
#                 else:
#                     endpoints[f"{method.upper()} {path}"] = request.build_absolute_uri(path)

#         serializer = ApiSchemaSerializer({"endpoints": endpoints})
#         return Response(serializer.data)
