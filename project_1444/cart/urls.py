# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from . import views

# router = DefaultRouter()
# router.register(r'cart', views.CartViewSet, basename='cart')

# urlpatterns = [
#     path('api/', include(router.urls)),
#     path('cart/add/<int:subproduct_id>/', views.add_to_cart, name='add_to_cart'),
#     path('cart/', views.cart_view, name='cart_view'),
#     path('cart/remove/<int:cart_id>/', views.remove_from_cart, name='remove_from_cart'),
#     path('checkout/', views.checkout_view, name='checkout'),
#     path('order/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
# ]
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CartViewSet
# from users.views import UserProfileView

router = DefaultRouter()
router.register(r"cart", CartViewSet, basename="cart")

urlpatterns = [
    path("", include(router.urls)),
    path('api/', include(router.urls)),
    path("total-price/", CartViewSet.as_view({"get": "total_price"}), name="total-price"),
    
]
