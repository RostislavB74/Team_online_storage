import hashlib

from django.conf import settings
from django.core.exceptions import FieldError
from django.utils import timezone
from django.utils.http import http_date, urlencode
from rest_framework.response import Response


class MixinCacheHeaders:

    def get_etag(self):
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
        return hashlib.sha1(etag_source.encode()).hexdigest()

    def get_cache_data(self):
        """Отримати останній оновлений об'єкт і створити кеш-значення"""
        try:
            latest_object = self.get_queryset().order_by("-updated_at").first()
        except FieldError:
            latest_object = None
        last_modified = latest_object.updated_at if latest_object else timezone.now()
        return last_modified, self.get_etag()

    def add_cache_headers(self, response: Response):
        """Attach cache headers to the response"""
        last_modified, etag = self.get_cache_data()
        response["Last-Modified"] = http_date(last_modified.timestamp())
        if etag:
            response["ETag"] = etag
        return response
