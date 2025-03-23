from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, RingSizeLookup, ProductAPIList, ProductAPIUpdate
from .views import CategoriesAPIList, CategoriesViewSet, CategoriesAPIUpdate, CategoriesAPIList
from .views import SubProductsSizesViewSet, TotalProductsViewSet

router = DefaultRouter()


router.register(r'products', ProductViewSet, basename='products')
router.register(r'categories', CategoriesViewSet, basename='categories')
router.register(r'subproducts', SubProductsSizesViewSet, basename='subproducts')
router.register(r'all-products', TotalProductsViewSet, basename='all-products')

urlpatterns = [
    path('', include(router.urls)),
    
    # path('sizetype/', CategoriesViewSet.as_view(), name='categories'),
    path('ring-size/', RingSizeLookup.as_view(), name='ring-size-lookup'),  # Додаємо окремо
    # path("", include(router.urls)),
]
