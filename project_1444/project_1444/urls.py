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
from product.views import (
    ProductAPIList,
    ProductAPIUpdate,
    CategoriesAPIList,
    CategoriesAPIDetail,
    ProductAPIDetail,
    SubProductsSizesViewSet,
    TotalProductsViewSet,
)
from product.views import RingSizeLookup
from discounts.views import AvailableDiscountsView
from .views import ApiRootView


urlpatterns = [
    path("api/", ApiRootView.as_view(), name="api-root"),
    path("admin/", admin.site.urls),
    path("api/v0/", include("mock.urls")),
    path("api/v1/", include("order.urls")),
    path("api/v1/", include("cart.urls")),
    path("api/v1/", include("product.urls")),
    path("api/v1/auth/", include("rest_framework.urls")),
    path("api/v1/", include("discounts.urls")),
    # path("api/v1/product/<int:pk>", ProductAPIDetail.as_view()),
    # path(
    #     "api/v1/all-products/<int:pk>",
    #     TotalProductsViewSet.as_view({"get": "retrieve"}),
    # ),
    # # path("api/v1/categories/", CategoriesAPIList.as_view()),
    # # path("api/v1/categories/<int:pk>", CategoriesAPIDetail.as_view()),
    # path("api/v1/subproducts/", SubProductsSizesViewSet.as_view({"get": "list"})),
    # path("api/v1/ring-size/", RingSizeLookup.as_view(), name="ring-size-lookup"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),  # JSON схема API
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),  # Swagger UI
    path(
        "api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"
    ),  # ReDoc
    path("api/v1/livez/", HealthCheckView.as_view(), name="livez"),
    path("api/v1/version/", VersionView.as_view(), name="version"),
]

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
