from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, CreateOrderFromCartView, HealthCheckView

router = DefaultRouter()
router.register(r"orders", OrderViewSet, basename="order")

urlpatterns = [
    path("", include(router.urls)),
    # path('create_order_from_cart/', CreateOrderFromCartView.as_view(), name='create_order_from_cart'),
    path('create/', CreateOrderFromCartView.as_view(), name='create_order_from_cart'),
    path('livez/', HealthCheckView.as_view(), name='livez'),
]
