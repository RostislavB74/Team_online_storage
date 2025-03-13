import hashlib

from django.core.exceptions import FieldError
from django.utils import timezone
from django.utils.http import http_date
from rest_framework.response import Response


class MixinCacheHeaders:

    def get_cache_data(self):
        """Отримати останній оновлений об'єкт і створити кеш-значення"""
        try:
            latest_object = self.get_queryset().order_by("-updated_at").first()
        except FieldError:
            latest_object = None

        if latest_object:
            last_modified = latest_object.updated_at
            etag = hashlib.md5(str(last_modified).encode()).hexdigest()
        else:
            last_modified = timezone.now()
            etag = None  # або можна задати дефолтне значення

        return last_modified, etag

    def add_cache_headers(self, response: Response):
        """Attach cache headers to the response"""
        last_modified, etag = self.get_cache_data()
        response["Last-Modified"] = http_date(last_modified.timestamp())
        if etag:
            response["ETag"] = etag
        return response
