from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, RingSizeLookup
from .views import  CategoriesViewSet
from .views import SubProductsSizesViewSet, TotalProductsViewSet, DescriptionViewSet, SubCategoriesViewSet

router = DefaultRouter()


router.register(r'product', ProductViewSet, basename='product')
router.register(r'categories', CategoriesViewSet, basename='categories')
router.register(r'subproducts', SubProductsSizesViewSet, basename='subproducts')
router.register(r'subcategories', SubCategoriesViewSet, basename='subcategories')
router.register(r'all-products', TotalProductsViewSet, basename='all-products')
router.register(r'description', DescriptionViewSet, basename='description')

urlpatterns = [
    path('', include(router.urls)),
    
    # path('sizetype/', CategoriesViewSet.as_view(), name='categories'),
    path('ring-size/', RingSizeLookup.as_view(), name='ring-size-lookup'),  # Додаємо окремо
    # path("", include(router.urls)),
]
