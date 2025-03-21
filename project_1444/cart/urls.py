from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CartViewSet
from users.views import UserProfileView

router = DefaultRouter()
router.register(r"cart", CartViewSet, basename="cart")

urlpatterns = [
    path("", include(router.urls)),
    path("profile/", UserProfileView.as_view(), name="user-profile"),
]