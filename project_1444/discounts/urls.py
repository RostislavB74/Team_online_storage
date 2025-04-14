
from django.urls import path
from .views import AvailableDiscountsView
from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()


# router.register(r'product', ProductViewSet, basename='product')
# router.register(r'categories', CategoriesViewSet, basename='categories')
# router.register(r'subproducts', SubProductsSizesViewSet, basename='subproducts')
# router.register(r'all-products', TotalProductsViewSet, basename='all-products')
# router.register(r'description', DescriptionViewSet, basename='description')

urlpatterns = [
    path('', include(router.urls)),

    path('my/', AvailableDiscountsView.as_view(), name='user-available-discounts'),
]