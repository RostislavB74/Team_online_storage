
from django.urls import path
from .views import AvailableDiscountsView

urlpatterns = [
    path('my/', AvailableDiscountsView.as_view(), name='user-available-discounts'),
]