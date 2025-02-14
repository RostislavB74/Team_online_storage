from django.urls import path
from .views import OTPRequestView, OTPVerifyView

urlpatterns = [
    path('send-otp/', OTPRequestView.as_view(), name='send-otp'),
    path('verify-otp/', OTPVerifyView.as_view(), name='verify-otp'),
]