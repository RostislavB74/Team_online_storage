import hashlib
from datetime import datetime, UTC

from django.conf import settings
from django.core.exceptions import FieldError
from django.http import HttpResponseNotModified, HttpResponse
from django.utils import timezone
from django.utils.http import http_date, urlencode, parse_http_date
from rest_framework.response import Response


class MixinCacheHeaders:
    _CACHE_HEADERS_LAST_MODIFIED_ENABLED = False
    _CACHE_CONTROL = "max-age=10, stale-while-revalidate=5"

    def get_etag(self, last_modified: str = None) -> str:
        """Generate ETag based on query params and language"""
        query_params = self.request.query_params  # Convert to dictionary
        lang: str = (
            self.request.headers.get("Accept-Language", settings.LANGUAGE_CODE)
            .split(",")[0]
            .strip()[:6]
        )
        # Sort query params to ensure consistent hashing
        sorted_query = urlencode(sorted(query_params.items()), doseq=True)

        # Create a hash from query params + language
        etag_source = f"{sorted_query}|{lang}"
        if last_modified:
            etag_source += f"|{last_modified}"
        return hashlib.sha1(etag_source.encode()).hexdigest()

    def get_cache_data(
        self,
        last_modified_tag_enabled: bool = True,
    ) -> dict[str, str]:
        """Отримати останній оновлений об'єкт і створити кеш-значення"""
        try:
            latest_object = self.get_queryset().order_by("-updated_at").first()
        except FieldError:
            latest_object = None
        last_modified = latest_object.updated_at if latest_object else timezone.now()
        last_modified = http_date(last_modified.timestamp())
        return {
            "Last-Modified": last_modified,
            "ETag": self.get_etag(last_modified),
        }

    def add_cache_headers(
        self,
        response: Response,
        cache_data: dict[str, str] | None = None,
        enabled: bool = settings.CACHE_HEADERS_ENABLED,
    ):
        if not enabled:
            return response
        """Attach cache headers to the response"""
        if cache_data is None:
            cache_data = self.get_cache_data()
        if self._CACHE_HEADERS_LAST_MODIFIED_ENABLED:
            response["Last-Modified"] = cache_data.get("Last-Modified")
        else:
            response["ETag"] = cache_data.get("ETag")
        response["Cache-Control"] = self._CACHE_CONTROL
        return response

    def check_cache_headers(
        self, request, enabled: bool = settings.CACHE_HEADERS_ENABLED
    ) -> HttpResponse | dict[str, str] | None:
        if not enabled:
            return None

        cache_data = self.get_cache_data()
        etag = cache_data.get("ETag")
        last_modified = cache_data.get("Last-Modified")

        if_none_match = request.META.get("HTTP_IF_NONE_MATCH")
        if_modified_since = request.META.get("HTTP_IF_MODIFIED_SINCE")

        if if_none_match and if_none_match == etag:
            return HttpResponseNotModified()

        if self._CACHE_HEADERS_LAST_MODIFIED_ENABLED and if_modified_since:
            try:
                if_modified_since_time = datetime.fromtimestamp(
                    parse_http_date(if_modified_since), UTC
                )
                if if_modified_since_time >= datetime.fromtimestamp(
                    parse_http_date(last_modified), UTC
                ):
                    return HttpResponseNotModified()
            except (TypeError, ValueError):
                ...  # Malformed header, ignore it.

        return {
            "Last-Modified": last_modified,
            "ETag": etag,
        }
