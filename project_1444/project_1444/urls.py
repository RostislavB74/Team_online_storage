from django.urls import path, include
from django.contrib import admin
from django.views.generic import RedirectView
from django.contrib.staticfiles.urls import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from .views import ApiRootView
from utils.views import HealthCheckView, VersionView
from django.conf import settings

admin.site.site_header = "VEVELLY"
admin.site.site_title = "Адмінка"
admin.site.index_title = "Ласкаво просимо"
admin.site.login_template = "custom_admin/login.html"

urlpatterns = [
    path("api/", ApiRootView.as_view(), name="api-root"),
    path("admin/", admin.site.urls, name="admin"),
    path("", include("users.urls")),
    path("", RedirectView.as_view(url="api/docs/", permanent=False), name="index"),
    path("social-auth/", include("social_django.urls", namespace="social")),
    path("api/v1/", include("order.urls")),
    path("api/v1/", include("cart.urls")),
    path("api/v1/", include("product.urls")),
    path("api/v1/auth/", include("rest_framework.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("api/v1/livez/", HealthCheckView.as_view(), name="livez"),
    path("api/v1/version/", VersionView.as_view(), name="version"),
    path("api/v1/", include("discounts.urls", namespace="discounts")),
]

if settings.STATIC_URL:
    other_static_files = ["favicon.ico", "robots.txt"]
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
    if settings.DEBUG_TOOLBAR_ENABLE:
        try:
            import debug_toolbar

            urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]
        except ImportError:
            print("debug_toolbar module is not imported")
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# from django.conf import settings
# from django.conf.urls.static import static
# from django.contrib import admin
# from django.urls import path, include
# from django.utils.translation import gettext_lazy as _
# from django.views.generic import RedirectView
# from drf_spectacular.views import (
#     SpectacularAPIView,
#     SpectacularSwaggerView,
#     SpectacularRedocView,
# )

# from utils.views import HealthCheckView, VersionView
# from .views import ApiRootView

# # from product.views import (
# # ProductAPIList,
# # ProductAPIUpdate,
# # CategoriesAPIList,
# # CategoriesAPIDetail,
# # ProductAPIDetail,
# # SubProductsSizesViewSet,
# # TotalProductsViewSet,
# # )
# # from product.views import RingSizeLookup
# # from discounts.views import AvailableDiscountsView

# # urls.py
# admin.site.site_header = "VEVELLY"
# admin.site.site_title = _("Адмінка")
# admin.site.index_title = _("Ласкаво просимо")
# admin.site.login_template = "custom_admin/login.html"

# urlpatterns = [

#     path("api/", ApiRootView.as_view(), name="api-root"),
#     path("admin/", admin.site.urls, name="admin"),
#     path("", include("users.urls")),
#     path("", RedirectView.as_view(url="api/docs/", permanent=False), name="index"),
#     path("social-auth/", include("social_django.urls", namespace="social")),
#     # path("api/v0/", include("mock.urls")),
#     path("api/v1/", include("order.urls")),
#     path("api/v1/", include("cart.urls")),
#     path("api/v1/", include("product.urls")),
#     path("api/v1/auth/", include("rest_framework.urls")),
#     path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
#     path(
#         "api/schema/swagger-ui/",
#         SpectacularSwaggerView.as_view(url_name="schema"),
#         name="swagger-ui",
#     ),
#     path(
#         "api/schema/redoc/",
#         SpectacularRedocView.as_view(url_name="schema"),
#         name="redoc",
#     ),
#     path(
#         "api/docs/",
#         SpectacularSwaggerView.as_view(url_name="schema"),
#         name="swagger-ui",
#     ),
#     path(
#         "api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"
#     ),  # ReDoc
#     path("api/v1/livez/", HealthCheckView.as_view(), name="livez"),
#     path("api/v1/version/", VersionView.as_view(), name="version"),
#     path(
#         "api/v1/",
#         include(
#             [
#                 path("discounts/", include("discounts.urls", namespace="discounts")),
#             ]
#         ),
#     ),
# ]

# if settings.STATIC_URL:
#     # Redirect other static files (favicon.ico, robots.txt)
#     other_static_files = [
#         "favicon.ico",
#         "robots.txt",
#     ]
#     for file in other_static_files:
#         if settings.STATIC_ROOT.joinpath(file).exists():
#             urlpatterns.append(
#                 path(
#                     file,
#                     RedirectView.as_view(
#                         url=f"{settings.STATIC_URL}{file}", permanent=True
#                     ),
#                 )
#             )


# if settings.DEBUG:
#     if settings.DEBUG_TOOLBAR_ENABLE:
#         try:
#             import debug_toolbar  # noqa

#             urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]
#         except ImportError:
#             print("debug_toolbar module is not imported")
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
