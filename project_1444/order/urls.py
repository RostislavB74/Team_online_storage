from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, HealthCheckView, VersionView

router = DefaultRouter()
router.register(r"orders", OrderViewSet, basename="order")

urlpatterns = [
    path("", include(router.urls)),
    path("livez/", HealthCheckView.as_view(), name="livez"),
    path("version/", VersionView.as_view(), name="version"),
]