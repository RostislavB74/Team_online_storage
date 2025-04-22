from django.urls import path
from .views import (
    LoginAPIView, RegisterAPIView, VerifyOTPAPIView,
    ProfileAPIView, LogoutAPIView, NotificationSettingsAPIView
)
from rest_framework.authtoken.views import ObtainAuthToken

urlpatterns = [
    path('auth/login/', LoginAPIView.as_view(), name='api_login'),
    path('auth/register/', RegisterAPIView.as_view(), name='api_register'),
    path('verify-otp/', VerifyOTPAPIView.as_view(), name='api_verify_otp'),
    path('profile/', ProfileAPIView.as_view(), name='api_profile'),
    path('notifications/', NotificationSettingsAPIView.as_view(), name='api_notifications'),
    path('auth/logout/', LogoutAPIView.as_view(), name='api_logout'),
    path('auth/token/', ObtainAuthToken.as_view(), name='api_token'),
]
