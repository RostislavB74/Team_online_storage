from django.urls import path
from .views import CartViewSet

urlpatterns = [
    path("", CartViewSet.as_view({"get": "list"}), name="cart-detail"),
    path("add/", CartViewSet.as_view({"post": "add_item"}), name="cart-add"),
    path("remove/<int:pk>/", CartViewSet.as_view({"delete": "remove_item"}), name="cart-remove"),
    path("clear/", CartViewSet.as_view({"post": "clear_cart"}), name="cart-clear"),
]
