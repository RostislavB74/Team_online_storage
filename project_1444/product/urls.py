from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, RingSizeLookup, ProductAPIList, ProductAPIUpdate, CategoriesAPIList, CategoriesViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='products')
# router.register(r'categories', CategoriesViewSet, basename='categories')

urlpatterns = [
    path('', include(router.urls)),
    path('categories/', CategoriesViewSet.as_view(), name='categories'),
    path('ring-size/', RingSizeLookup.as_view(), name='ring-size-lookup'),  # Додаємо окремо
]
