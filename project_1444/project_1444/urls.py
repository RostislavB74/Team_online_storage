"""
URL configuration for project_1444 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)


from utils.views import HealthCheckView, VersionView

from .views import ApiRootView

from debug_toolbar.toolbar import debug_toolbar_urls

# from product.views import (
# ProductAPIList,
# ProductAPIUpdate,
# CategoriesAPIList,
# CategoriesAPIDetail,
# ProductAPIDetail,
# SubProductsSizesViewSet,
# TotalProductsViewSet,
# )
# from product.views import RingSizeLookup
# from discounts.views import AvailableDiscountsView

from .views import ApiRootView

from debug_toolbar.toolbar import debug_toolbar_urls

# urls.py
admin.site.site_header = "VEVELLY"
admin.site.site_title = "Адмінка"
admin.site.index_title = "Ласкаво просимо"
admin.site.login_template = "custom_admin/login.html"

urlpatterns = [
    path("api/", ApiRootView.as_view(), name="api-root"),
    path("admin/", admin.site.urls, name="admin"),
    path("", include("users.urls")),
    path("social-auth/", include("social_django.urls", namespace="social")),
    path("api/v0/", include("mock.urls")),
    path("api/v1/", include("order.urls")),
    path("api/v1/", include("cart.urls")),
    path("api/v1/", include("product.urls")),
    path("api/v1/auth/", include("rest_framework.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"
    ),  # ReDoc
    path("api/v1/livez/", HealthCheckView.as_view(), name="livez"),
    path("api/v1/version/", VersionView.as_view(), name="version"),
    path(
        "api/v1/",
        include(
            [
                path("discounts/", include("discounts.urls", namespace="discounts")),
            ]
        ),
    ),
]
# Додаємо debug_toolbar, якщо в дебаг-режимі
if "debug_toolbar" in settings.INSTALLED_APPS:
    urlpatterns += [path("__debug__/", include("debug_toolbar.urls"))]


if settings.STATIC_URL:
    # Redirect other static files (favicon.ico, robots.txt)
    other_static_files = [
        "favicon.ico",
        "robots.txt",
    ]
    for file in other_static_files:
        if settings.STATIC_ROOT.joinpath(file).exists():
            urlpatterns.append(
                path(
                    file,
                    RedirectView.as_view(
                        url=f"{settings.STATIC_URL}{file}", permanent=True
                    ),
                )
            )


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
