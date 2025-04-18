# from django.urls import path
# from .views import OTPRequestView, OTPVerifyView

# urlpatterns = [
#     path('send-otp/', OTPRequestView.as_view(), name='send-otp'),
#     path('verify-otp/', OTPVerifyView.as_view(), name='verify-otp'),
# ]
from django.urls import path, include
from rest_framework.routers import DefaultRouter
# from users.views import UserProfileView

from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('api/token/', views.CustomAuthToken.as_view(), name='api_token'),
]
# router = DefaultRouter()

# path("profile/", UserProfileView.as_view(), name="user-profile"),