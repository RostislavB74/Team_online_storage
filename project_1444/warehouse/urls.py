from rest_framework.routers import DefaultRouter
from .views import WarehouseViewSet, WarehouseStockViewSet, ReservationViewSet
from django.urls import path, include


router = DefaultRouter()
router.register(r'warehouses', WarehouseViewSet)
router.register(r'warehouse-stock', WarehouseStockViewSet)
router.register(r'reservations', ReservationViewSet)

urlpatterns = [
    path('api/v1/', include(router.urls)),
]

