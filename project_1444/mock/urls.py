from django.urls import path, include
from django.urls import re_path
from mock.views import MockViewApiV0


urlpatterns = [
    re_path(
        r"^(?:.*)/?$", MockViewApiV0.as_view(), name="mock-lookup"
    ),  # Catch all routes
]
