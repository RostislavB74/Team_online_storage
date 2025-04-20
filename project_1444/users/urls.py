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
# from django.urls import path
# from .views import (
#     LoginAPIView, RegisterAPIView, VerifyOTPAPIView,
#     ProfileAPIView, LogoutAPIView
# )
# from rest_framework.authtoken.views import ObtainAuthToken

# urlpatterns = [
#     path('auth/login/', LoginAPIView.as_view(), name='api_login'),
#     path('auth/register/', RegisterAPIView.as_view(), name='api_register'),
#     path('verify-otp/', VerifyOTPAPIView.as_view(), name='api_verify_otp'),
#     path('profile/', ProfileAPIView.as_view(), name='api_profile'),
#     path('auth/logout/', LogoutAPIView.as_view(), name='api_logout'),
#     path('auth/token/', ObtainAuthToken.as_view(), name='api_token'),
# ]
# # from django.urls import path
# # from .views import OTPRequestView, OTPVerifyView

# # urlpatterns = [
# #     path('send-otp/', OTPRequestView.as_view(), name='send-otp'),
# #     path('verify-otp/', OTPVerifyView.as_view(), name='verify-otp'),
# # ]
# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# # from users.views import UserProfileView

# from django.urls import path
# from . import views

# urlpatterns = [
#     path('login/', views.login_view, name='login'),
#     path('verify-otp/', views.verify_otp, name='verify_otp'),
#     path('register/', views.register_view, name='register'),
#     path('logout/', views.logout_view, name='logout'),
#     path('profile/', views.profile_view, name='profile'),
#     path('api/token/', views.CustomAuthToken.as_view(), name='api_token'),
# ]
# router = DefaultRouter()

# path("profile/", UserProfileView.as_view(), name="user-profile"),