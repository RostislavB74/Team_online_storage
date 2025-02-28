# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from .views import ProductViewSet, RingSizeLookup

# router = DefaultRouter()
# router.register(r'product', RingSizeLookup, basename='product-list')

# urlpatterns = [
#     path('', include(router.urls)),
   
# ]
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, RingSizeLookup

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='products')

urlpatterns = [
    path('', include(router.urls)),
    path('ring-size/', RingSizeLookup.as_view(), name='ring-size-lookup'),  # Додаємо окремо
]
