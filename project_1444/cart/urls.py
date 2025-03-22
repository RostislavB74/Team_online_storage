from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CartViewSet
# from users.views import UserProfileView

router = DefaultRouter()
router.register(r"cart", CartViewSet, basename="cart")

urlpatterns = [
    path("", include(router.urls)),
    # path("total-price/", CartViewSet.as_view({"get": "total_price"}), name="total-price"),
    
]