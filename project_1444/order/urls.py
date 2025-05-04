from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, UpdateOrderStatusAPIView, LiqPayCallbackAPIView


router = DefaultRouter()
router.register(r"orders", OrderViewSet, basename="order")

urlpatterns = [
    path("", include(router.urls)),
    path('orders/<int:order_id>/update-status/', UpdateOrderStatusAPIView.as_view(), name='update_order_status'),
    path('orders/liqpay/callback/', LiqPayCallbackAPIView.as_view(), name='liqpay_callback'),
]