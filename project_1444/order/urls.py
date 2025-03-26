from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet


class NoSlashRouter(DefaultRouter):
    """Custom router that removes the enforced trailing slash."""

    trailing_slash = ""


router = NoSlashRouter()  # Use this instead of DefaultRouter

# router = DefaultRouter()
router.register(r"orders", OrderViewSet, basename="order")

urlpatterns = [
    path("", include(router.urls)),
]
